import logging
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
)

from .models import Bank, BankAccount, BankTransaction
from .serializers import (
    AddMoneySerializer,
    BankAccountSerializer,
    BankSerializer,
    BankTransactionSerializer,
    WithdrawSerializer,
)

logger = logging.getLogger("banking")


class BankListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        banks = Bank.objects.filter(is_islamic=True, is_active=True)
        return Response(BankSerializer(banks, many=True).data)


class BankAccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        accounts = BankAccount.objects.filter(user=request.user).select_related("bank")
        return Response(BankAccountSerializer(accounts, many=True).data)

    def post(self, request):
        serializer = BankAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save(user=request.user)
        return Response(BankAccountSerializer(account).data, status=status.HTTP_201_CREATED)


class BankAccountDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            account = BankAccount.objects.get(pk=pk, user=request.user)
        except BankAccount.DoesNotExist:
            return error_response("Account not found.", 404)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = AddMoneySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bank_account_id = serializer.validated_data["bank_account_id"]
        amount = serializer.validated_data["amount"]

        try:
            bank_account = BankAccount.objects.get(id=bank_account_id, user=request.user)
        except BankAccount.DoesNotExist:
            return error_response("Bank account not found.")

        credit_wallet(request.user, amount)

        txn = BankTransaction.objects.create(
            user=request.user,
            bank_account=bank_account,
            amount=amount,
            fee=Decimal("0.00"),
            transaction_type="add_money",
            status="completed",
        )

        bank_name = bank_account.bank.name
        record_transaction(
            receiver=request.user,
            transaction_type="bank",
            amount=amount,
            fee=Decimal("0.00"),
            note=f"Added money from {bank_name}",
            counterparty=bank_name,
            receiver_message=(
                f"You added ৳{amount} from {bank_name} account ending "
                f"{bank_account.account_number[-4:]}."
            ),
        )

        logger.info(
            "AddMoney: user=%s bank=%s account=%s amount=%s ref=%s",
            request.user.phone,
            bank_account.bank.name,
            bank_account.account_number[-4:],
            amount,
            txn.reference,
        )
        return Response(BankTransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bank_account_id = serializer.validated_data["bank_account_id"]
        amount = serializer.validated_data["amount"]

        try:
            bank_account = BankAccount.objects.get(id=bank_account_id, user=request.user)
        except BankAccount.DoesNotExist:
            return error_response("Bank account not found.")

        fee = (amount * Decimal("0.5") / Decimal("100")).quantize(Decimal("0.01"))
        total = amount + fee

        wallet = locked_deduct_wallet(request.user, total)
        if wallet is None:
            return error_response("Insufficient balance.")

        txn = BankTransaction.objects.create(
            user=request.user,
            bank_account=bank_account,
            amount=amount,
            fee=fee,
            transaction_type="withdraw",
            status="completed",
        )

        bank_name = bank_account.bank.name
        record_transaction(
            sender=request.user,
            transaction_type="bank",
            amount=amount,
            fee=fee,
            note=f"Withdrew to {bank_name}",
            counterparty=bank_name,
            sender_message=(
                f"You withdrew ৳{amount} (fee ৳{fee}) to {bank_name} account ending "
                f"{bank_account.account_number[-4:]}."
            ),
        )

        logger.info(
            "Withdraw: user=%s bank=%s account=%s amount=%s fee=%s ref=%s",
            request.user.phone,
            bank_account.bank.name,
            bank_account.account_number[-4:],
            amount,
            fee,
            txn.reference,
        )
        return Response(BankTransactionSerializer(txn).data, status=status.HTTP_201_CREATED)


class BankTransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            BankTransaction.objects.filter(user=request.user)
            .select_related("bank_account__bank")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": BankTransactionSerializer(p["queryset"], many=True).data,
            }
        )
