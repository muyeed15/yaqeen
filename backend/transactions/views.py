import logging
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User, Wallet
from common.pagination import get_page, get_page_size, paginate
from common.utils import daily_spent, error_response
from notifications.models import Notification
from transactions.models import MoneyRequest, Transaction
from transactions.serializers import (
    CreateMoneyRequestSerializer,
    MoneyRequestSerializer,
    TransactionSerializer,
    TransferSerializer,
)

logger = logging.getLogger("transactions")


def _transaction_qs(user):
    return (
        Transaction.objects.filter(Q(sender=user) | Q(receiver=user))
        .select_related("sender", "receiver", "merchant")
        .only(
            "id",
            "reference_id",
            "sender__phone",
            "receiver__phone",
            "merchant__business_name",
            "counterparty",
            "amount",
            "fee",
            "transaction_type",
            "status",
            "note",
            "created_at",
        )
        .order_by("-created_at")
    )


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = paginate(
            _transaction_qs(request.user), get_page(request), get_page_size(request)
        )
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": TransactionSerializer(p["queryset"], many=True).data,
            }
        )


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            tx = _transaction_qs(request.user).get(pk=pk)
        except Transaction.DoesNotExist:
            return error_response("Not found.", 404)
        return Response(TransactionSerializer(tx).data)


class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receiver_phone = serializer.validated_data["receiver_phone"]
        amount = serializer.validated_data["amount"]
        note = serializer.validated_data["note"]

        if receiver_phone == request.user.phone:
            return error_response("Cannot transfer to yourself.")

        fee_rate = Decimal(str(settings.TRANSFER_FEE_PERCENT)) / Decimal("100")
        fee = (amount * fee_rate).quantize(Decimal("0.01"))
        total_debit = amount + fee

        try:
            with transaction.atomic():
                sender_wallet = Wallet.objects.select_for_update().get(
                    user=request.user
                )
                try:
                    receiver_wallet = (
                        Wallet.objects.select_for_update()
                        .select_related("user")
                        .get(user__phone=receiver_phone)
                    )
                except ObjectDoesNotExist:
                    raise ValueError("Recipient account not found.")

                if sender_wallet.status != "active":
                    raise ValueError("Your wallet is frozen.")
                if receiver_wallet.status != "active":
                    raise ValueError("Receiver's wallet is frozen.")
                if sender_wallet.balance < total_debit:
                    raise ValueError(
                        f"Insufficient balance. Required: ৳{total_debit} "
                        f"(৳{amount} + ৳{fee} fee)."
                    )

                today = timezone.now().date()
                spent_today = daily_spent(request.user, today)
                if spent_today + total_debit > sender_wallet.daily_limit:
                    remaining = max(
                        sender_wallet.daily_limit - spent_today, Decimal("0")
                    )
                    raise ValueError(
                        f"Daily limit exceeded. Remaining today: ৳{remaining}."
                    )

                sender_wallet.balance -= total_debit
                receiver_wallet.balance += amount
                sender_wallet.save(update_fields=["balance"])
                receiver_wallet.save(update_fields=["balance"])

                tx = Transaction.objects.create(
                    sender=request.user,
                    receiver=receiver_wallet.user,
                    amount=amount,
                    fee=fee,
                    transaction_type="send",
                    status="completed",
                    note=note,
                )

                Notification.objects.bulk_create(
                    [
                        Notification(
                            user=request.user,
                            message=(
                                f"You sent ৳{amount} to {receiver_phone}. "
                                f"Fee: ৳{fee}. Ref: {tx.reference_id}"
                            ),
                        ),
                        Notification(
                            user=receiver_wallet.user,
                            message=(
                                f"You received ৳{amount} from {request.user.phone}. "
                                f"Ref: {tx.reference_id}"
                            ),
                        ),
                    ]
                )

        except (ValueError, ObjectDoesNotExist) as e:
            logger.warning(
                "TransferView: %s, user=%s to=%s amount=%s",
                e,
                request.user.phone,
                receiver_phone,
                amount,
            )
            return error_response(str(e))

        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)


class MoneyRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            MoneyRequest.objects.filter(
                Q(requester=request.user) | Q(target=request.user)
            )
            .select_related("requester", "target")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": MoneyRequestSerializer(p["queryset"], many=True).data,
            }
        )


class CreateMoneyRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateMoneyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_phone = serializer.validated_data["phone"]
        amount = serializer.validated_data["amount"]

        if target_phone == request.user.phone:
            return error_response("Cannot request money from yourself.")

        try:
            target = User.objects.get(phone=target_phone)
        except User.DoesNotExist:
            return error_response("User not found.")

        money_req = MoneyRequest.objects.create(
            requester=request.user,
            target=target,
            amount=amount,
            note=serializer.validated_data.get("note", ""),
        )

        Notification.objects.create(
            user=target,
            message=(f"{request.user.phone} requested ৳{amount} from you. "),
        )

        return Response(
            MoneyRequestSerializer(money_req).data, status=status.HTTP_201_CREATED
        )


class RespondMoneyRequestView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        action = request.data.get("action")

        try:
            money_req = MoneyRequest.objects.get(
                pk=pk, target=request.user, status="pending"
            )
        except MoneyRequest.DoesNotExist:
            return error_response("Money request not found or already handled.", 404)

        if action == "accept":
            fee_rate = Decimal(str(settings.TRANSFER_FEE_PERCENT)) / Decimal("100")
            fee = (money_req.amount * fee_rate).quantize(Decimal("0.01"))
            total = money_req.amount + fee

            sender_wallet = Wallet.objects.select_for_update().get(user=request.user)
            receiver_wallet = Wallet.objects.select_for_update().get(
                user=money_req.requester
            )

            if sender_wallet.status != "active":
                return error_response("Your wallet is frozen.")
            if sender_wallet.balance < total:
                return error_response("Insufficient balance.")

            sender_wallet.balance -= total
            receiver_wallet.balance += money_req.amount
            sender_wallet.save(update_fields=["balance"])
            receiver_wallet.save(update_fields=["balance"])

            Transaction.objects.create(
                sender=request.user,
                receiver=money_req.requester,
                amount=money_req.amount,
                fee=fee,
                transaction_type="send",
                status="completed",
                note=f"Request: {money_req.note}"
                if money_req.note
                else "Money request",
            )

            money_req.status = "accepted"
            money_req.save(update_fields=["status"])

            Notification.objects.bulk_create(
                [
                    Notification(
                        user=request.user,
                        message=f"You fulfilled ৳{money_req.amount} request from {money_req.requester.phone}.",
                    ),
                    Notification(
                        user=money_req.requester,
                        message=f"{request.user.phone} accepted your ৳{money_req.amount} request.",
                    ),
                ]
            )

            return Response(MoneyRequestSerializer(money_req).data)

        elif action == "decline":
            money_req.status = "declined"
            money_req.save(update_fields=["status"])

            Notification.objects.create(
                user=money_req.requester,
                message=f"{request.user.phone} declined your ৳{money_req.amount} request.",
            )
            return Response(MoneyRequestSerializer(money_req).data)

        return error_response("Action must be 'accept' or 'decline'.")
