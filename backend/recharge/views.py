import logging
import uuid
from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page, get_page_size, paginate
from common.utils import error_response, locked_deduct_wallet, record_transaction

from .models import DataPack, Operator, RechargeTransaction
from .serializers import (
    DataPackSerializer,
    OperatorSerializer,
    RechargeSerializer,
    RechargeTransactionSerializer,
)

logger = logging.getLogger("recharge")


class OperatorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operators = Operator.objects.filter(is_active=True)
        return Response(OperatorSerializer(operators, many=True, context={"request": request}).data)


class DataPackListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operator_id = request.query_params.get("operator_id")
        qs = DataPack.objects.filter(is_active=True)
        if operator_id:
            qs = qs.filter(operator_id=operator_id)
        return Response(DataPackSerializer(qs, many=True).data)


class RechargeView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = RechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        operator_id = serializer.validated_data["operator_id"]
        phone_number = serializer.validated_data["phone_number"]
        recharge_type = serializer.validated_data["recharge_type"]

        try:
            operator = Operator.objects.get(id=operator_id, is_active=True)
        except Operator.DoesNotExist:
            return error_response("Operator not found or inactive.")

        if recharge_type == "data_pack":
            pack_id = serializer.validated_data.get("data_pack_id")
            try:
                pack = DataPack.objects.get(id=pack_id, is_active=True)
            except DataPack.DoesNotExist:
                return error_response("Data pack not found or inactive.")
            amount = pack.amount
        else:
            amount = serializer.validated_data["amount"]

        fee = Decimal("0.00")
        total = amount + fee

        wallet = locked_deduct_wallet(request.user, total)
        if wallet is None:
            return error_response("Insufficient balance.")

        ref = "RCH" + uuid.uuid4().hex[:10].upper()
        txn = RechargeTransaction.objects.create(
            user=request.user,
            operator=operator,
            phone_number=phone_number,
            amount=amount,
            fee=fee,
            recharge_type=recharge_type,
            data_pack_id=serializer.validated_data.get("data_pack_id"),
            reference=ref,
            status="completed",
        )

        record_transaction(
            sender=request.user,
            transaction_type="recharge",
            amount=amount,
            fee=fee,
            note=f"{operator.name} {recharge_type.replace('_', ' ')} for {phone_number}",
            counterparty=operator.name,
            sender_message=(
                f"You recharged ৳{amount} for {phone_number} on {operator.name}. " f"Ref: {ref}"
            ),
        )

        logger.info(
            "Recharge: user=%s op=%s phone=%s type=%s amount=%s ref=%s",
            request.user.phone,
            operator.name,
            phone_number,
            recharge_type,
            amount,
            ref,
        )
        return Response(RechargeTransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


class RechargeHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            RechargeTransaction.objects.filter(user=request.user)
            .select_related("operator")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": RechargeTransactionSerializer(p["queryset"], many=True).data,
            }
        )
