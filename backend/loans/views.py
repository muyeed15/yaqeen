import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page, get_page_size, paginate
from common.utils import (
    credit_wallet,
    error_response,
    locked_deduct_wallet,
    record_transaction,
    user_objects_or_error,
)

from .models import QardHasanApplication, QardHasanProduct, QardHasanRepayment
from .serializers import (
    ApplyQardHasanSerializer,
    QardHasanApplicationSerializer,
    QardHasanProductSerializer,
    RepayQardHasanSerializer,
)

logger = logging.getLogger("loans")


class QardHasanProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = QardHasanProduct.objects.filter(is_active=True)
        return Response(QardHasanProductSerializer(products, many=True).data)


class ApplyQardHasanView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = ApplyQardHasanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        amount = serializer.validated_data["amount"]

        try:
            product = QardHasanProduct.objects.get(id=product_id, is_active=True)
        except QardHasanProduct.DoesNotExist:
            return error_response("Qard Hasan product not found or inactive.")

        if amount < product.min_amount or amount > product.max_amount:
            return error_response(
                f"Amount must be between ৳{product.min_amount} and ৳{product.max_amount}."
            )

        service_fee = product.service_fee
        amount_due = amount + service_fee

        if service_fee > 0:
            wallet = locked_deduct_wallet(request.user, service_fee)
            if wallet is None:
                return error_response("Insufficient balance for service fee.")

        application = QardHasanApplication.objects.create(
            user=request.user,
            product=product,
            amount=amount,
            service_fee=service_fee,
            amount_due=amount_due,
            tenure_days=product.tenure_days,
            status="disbursed",
            due_date=date.today() + timedelta(days=product.tenure_days),
        )

        credit_wallet(request.user, amount)

        if service_fee > 0:
            record_transaction(
                sender=request.user,
                transaction_type="loan",
                amount=service_fee,
                note=f"{product.name} service fee",
                counterparty=product.name,
                sender_message=(
                    f"Qard Hasan service fee of ৳{service_fee} charged for "
                    f"{product.name}."
                ),
            )

        record_transaction(
            receiver=request.user,
            transaction_type="loan",
            amount=amount,
            note=f"{product.name} disbursed",
            counterparty=product.name,
            receiver_message=(
                f"Qard Hasan of ৳{amount} disbursed to your wallet. "
                f"Ref: {application.loan_reference}"
            ),
        )

        logger.info(
            "ApplyQardHasan: user=%s product=%s amount=%s due=%s ref=%s",
            request.user.phone,
            product.name,
            amount,
            amount_due,
            application.loan_reference,
        )
        return Response(
            QardHasanApplicationSerializer(application).data,
            status=status.HTTP_201_CREATED,
        )


class QardHasanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            QardHasanApplication.objects.filter(user=request.user)
            .select_related("product")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": QardHasanApplicationSerializer(
                    p["queryset"], many=True
                ).data,
            }
        )


class QardHasanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        loan = user_objects_or_error(QardHasanApplication, id=pk, user=request.user)
        if loan is None:
            return error_response("Loan not found.", 404)
        return Response(QardHasanApplicationSerializer(loan).data)


class RepayQardHasanView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        loan = user_objects_or_error(QardHasanApplication, id=pk, user=request.user)
        if loan is None:
            return error_response("Loan not found.", 404)

        if loan.status not in ("disbursed", "overdue"):
            return error_response(f"Cannot repay loan with status: {loan.status}")

        serializer = RepayQardHasanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        hibah = Decimal(str(serializer.validated_data.get("hibah", 0)))
        total_pay = amount + hibah
        remaining = loan.amount_due - loan.amount_paid

        if amount > remaining:
            return error_response(f"Amount exceeds remaining balance of ৳{remaining}.")

        wallet = locked_deduct_wallet(request.user, total_pay)
        if wallet is None:
            return error_response("Insufficient balance.")

        QardHasanRepayment.objects.create(application=loan, amount=amount, hibah=hibah)

        note = f"Qard Hasan repayment {loan.loan_reference}"
        if hibah > 0:
            note += f" (hibah ৳{hibah})"
        record_transaction(
            sender=request.user,
            transaction_type="loan",
            amount=amount,
            note=note,
            counterparty=loan.product.name,
            sender_message=(f"You repaid ৳{amount} for {loan.loan_reference}."),
        )

        logger.info(
            "RepayQardHasan: user=%s ref=%s amount=%s hibah=%s paid=%s/%s",
            request.user.phone,
            loan.loan_reference,
            amount,
            hibah,
            loan.amount_paid,
            loan.amount_due,
        )
        return Response(QardHasanApplicationSerializer(loan).data)
