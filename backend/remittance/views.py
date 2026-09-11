import logging
from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page, get_page_size, paginate
from common.utils import credit_wallet, error_response, record_transaction

from .models import RemittancePartner, RemittanceTransaction
from .serializers import (
    ReceiveRemittanceSerializer,
    RemittancePartnerSerializer,
    RemittanceTransactionSerializer,
)

logger = logging.getLogger("remittance")


class PartnerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        partners = RemittancePartner.objects.filter(is_active=True)
        return Response(RemittancePartnerSerializer(partners, many=True).data)


class ReceiveRemittanceView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = ReceiveRemittanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        partner_id = serializer.validated_data["partner_id"]
        amount_foreign = serializer.validated_data["amount_foreign"]

        try:
            partner = RemittancePartner.objects.get(id=partner_id, is_active=True)
        except RemittancePartner.DoesNotExist:
            return error_response("Remittance partner not found or inactive.")

        amount_bdt = (amount_foreign * partner.exchange_rate).quantize(Decimal("0.01"))

        credit_wallet(request.user, amount_bdt)

        txn = RemittanceTransaction.objects.create(
            user=request.user,
            partner=partner,
            sender_name=serializer.validated_data["sender_name"],
            sender_country=serializer.validated_data["sender_country"],
            amount_foreign=amount_foreign,
            amount_bdt=amount_bdt,
            exchange_rate=partner.exchange_rate,
            status="completed",
        )

        record_transaction(
            receiver=request.user,
            transaction_type="remittance",
            amount=amount_bdt,
            fee=Decimal("0.00"),
            note=(
                f"Remittance from {txn.sender_name} ({txn.sender_country}) "
                f"via {partner.name}"
            ),
            counterparty=partner.name,
            receiver_message=(
                f"You received ৳{amount_bdt} from {txn.sender_name} via "
                f"{partner.name}. Ref: {txn.reference_number}"
            ),
        )

        logger.info(
            "Remittance: user=%s partner=%s foreign=%s %s bdt=%s ref=%s",
            request.user.phone,
            partner.name,
            amount_foreign,
            partner.currency,
            amount_bdt,
            txn.reference_number,
        )
        return Response(
            RemittanceTransactionSerializer(txn).data, status=status.HTTP_201_CREATED
        )


class RemittanceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            RemittanceTransaction.objects.filter(user=request.user)
            .select_related("partner")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": RemittanceTransactionSerializer(
                    p["queryset"], many=True
                ).data,
            }
        )
