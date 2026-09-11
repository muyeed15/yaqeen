import logging
import uuid

from django.db import transaction
from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page, get_page_size, paginate
from common.utils import error_response, locked_deduct_wallet, record_transaction

from .models import Biller, BillerCategory, BillPayment
from .serializers import BillerSerializer, BillPaymentSerializer, PayBillSerializer

logger = logging.getLogger("billpay")


class BillerCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        counts = (
            Biller.objects.filter(is_active=True)
            .values("category__key")
            .annotate(count=Count("id"))
        )
        counts_by_category = {c["category__key"]: c["count"] for c in counts}
        categories = [
            {
                "key": category.key,
                "label": category.label,
                "count": counts_by_category.get(category.key, 0),
            }
            for category in BillerCategory.objects.filter(is_active=True)
        ]
        return Response(categories)


class BillerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get("category")
        qs = Biller.objects.filter(is_active=True).select_related("category")
        if category:
            qs = qs.filter(category__key=category)
        return Response(
            BillerSerializer(qs, many=True, context={"request": request}).data
        )


class PayBillView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = PayBillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        biller_id = serializer.validated_data["biller_id"]
        account_number = serializer.validated_data["account_number"]
        amount = serializer.validated_data["amount"]

        try:
            biller = Biller.objects.get(id=biller_id, is_active=True)
        except Biller.DoesNotExist:
            return error_response("Biller not found or inactive.")

        wallet = locked_deduct_wallet(request.user, amount)
        if wallet is None:
            return error_response("Insufficient balance.")

        ref = "BILL" + uuid.uuid4().hex[:10].upper()
        payment = BillPayment.objects.create(
            user=request.user,
            biller=biller,
            account_number=account_number,
            bill_number=serializer.validated_data.get("bill_number", ""),
            amount=amount,
            bill_month=serializer.validated_data.get("bill_month", ""),
            reference=ref,
            status="completed",
        )

        record_transaction(
            sender=request.user,
            transaction_type="bill",
            amount=amount,
            note=f"{biller.name} bill {payment.bill_month}".strip(),
            counterparty=biller.name,
            sender_message=(
                f"You paid ৳{amount} to {biller.name} for account "
                f"{account_number}. Ref: {ref}"
            ),
        )

        logger.info(
            "BillPay: user=%s biller=%s account=%s amount=%s ref=%s",
            request.user.phone,
            biller.name,
            account_number,
            amount,
            ref,
        )
        return Response(
            BillPaymentSerializer(payment).data, status=status.HTTP_201_CREATED
        )


class BillHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            BillPayment.objects.filter(user=request.user)
            .select_related("biller")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": BillPaymentSerializer(p["queryset"], many=True).data,
            }
        )
