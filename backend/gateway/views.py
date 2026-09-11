import logging
from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import (
    credit_wallet,
    error_response,
    locked_deduct_wallet,
    record_transaction,
)

from .models import GatewayTransaction, PaymentGateway
from .serializers import GatewayTransactionSerializer

logger = logging.getLogger("gateway")


class GatewayInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        merchant_id = request.data.get("merchant_id")
        amount = request.data.get("amount")
        order_id = request.data.get("order_id", "")

        try:
            amount = Decimal(str(amount))
        except (TypeError, ValueError):
            return error_response("Invalid amount.")

        if amount <= 0:
            return error_response("Amount must be greater than zero.")

        try:
            gateway = PaymentGateway.objects.get(
                merchant_id=merchant_id, is_active=True
            )
        except PaymentGateway.DoesNotExist:
            return error_response("Invalid or inactive merchant gateway.", 404)

        fee = (amount * Decimal("1.5") / Decimal("100")).quantize(Decimal("0.01"))
        total = amount + fee

        wallet = locked_deduct_wallet(request.user, total)
        if wallet is None:
            return error_response("Insufficient balance.")

        credit_wallet(gateway.merchant.user, amount)

        txn = GatewayTransaction.objects.create(
            gateway=gateway,
            user=request.user,
            amount=amount,
            fee=fee,
            order_id=order_id,
            status="completed",
        )

        merchant_name = gateway.merchant.business_name
        record_transaction(
            sender=request.user,
            receiver=gateway.merchant.user,
            merchant=gateway.merchant,
            transaction_type="gateway",
            amount=amount,
            fee=fee,
            note=f"Gateway payment to {merchant_name}"
            + (f" (order {order_id})" if order_id else ""),
            counterparty=merchant_name,
            sender_message=(
                f"You paid ৳{amount} to {merchant_name} through the payment "
                f"gateway. Ref: {txn.txn_id}"
            ),
            receiver_message=(
                f"Gateway payment of ৳{amount} received at {merchant_name}. "
                f"Ref: {txn.txn_id}"
            ),
        )

        logger.info(
            "Gateway: user=%s merchant=%s amount=%s fee=%s txn=%s",
            request.user.phone,
            gateway.merchant.business_name,
            amount,
            fee,
            txn.txn_id,
        )
        return Response(
            GatewayTransactionSerializer(txn).data, status=status.HTTP_201_CREATED
        )


class GatewayStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, txn_id):
        try:
            txn = GatewayTransaction.objects.get(txn_id=txn_id, user=request.user)
        except GatewayTransaction.DoesNotExist:
            return error_response("Transaction not found.", 404)
        return Response(GatewayTransactionSerializer(txn).data)


class GatewayHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from common.pagination import get_page, get_page_size, paginate

        qs = (
            GatewayTransaction.objects.filter(user=request.user)
            .select_related("gateway__merchant")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": GatewayTransactionSerializer(p["queryset"], many=True).data,
            }
        )


class GatewayWebhookView(APIView):
    def post(self, request):
        api_key = request.headers.get("X-Api-Key")
        if not api_key:
            return error_response("Missing API key.", 401)

        try:
            PaymentGateway.objects.get(api_key=api_key, is_active=True)
        except PaymentGateway.DoesNotExist:
            return error_response("Invalid API key.", 401)

        return Response({"status": "ok"})
