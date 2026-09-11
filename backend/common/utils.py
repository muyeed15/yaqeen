from decimal import Decimal

from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response

from accounts.models import Wallet
from notifications.models import Notification
from transactions.models import Transaction


def daily_spent(user, today):
    return Transaction.objects.filter(
        sender=user,
        transaction_type__in=["send", "payment"],
        status="completed",
        created_at__date=today,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")


def locked_deduct_wallet(user, amount):
    wallet = Wallet.objects.select_for_update().get(user=user)
    if wallet.status != "active":
        return None
    if wallet.balance < amount:
        return None
    wallet.balance -= amount
    wallet.save(update_fields=["balance"])
    return wallet


def credit_wallet(user, amount):
    wallet = Wallet.objects.select_for_update().get(user=user)
    wallet.balance += amount
    wallet.save(update_fields=["balance"])
    return wallet


def record_transaction(
    *,
    sender=None,
    receiver=None,
    merchant=None,
    transaction_type,
    amount,
    fee=Decimal("0.00"),
    note="",
    counterparty="",
    sender_message=None,
    receiver_message=None,
):
    """Record a unified ledger entry and any related notifications.

    Must be called inside a ``transaction.atomic()`` block when it accompanies
    a wallet mutation so the ledger and balance stay in sync.
    """
    txn = Transaction.objects.create(
        sender=sender,
        receiver=receiver,
        merchant=merchant,
        transaction_type=transaction_type,
        amount=amount,
        fee=fee,
        note=note,
        counterparty=counterparty,
        status="completed",
    )

    notifications = []
    if sender is not None and sender_message:
        notifications.append(Notification(user=sender, message=sender_message))
    if receiver is not None and receiver_message:
        notifications.append(Notification(user=receiver, message=receiver_message))
    if notifications:
        Notification.objects.bulk_create(notifications)

    return txn


def user_objects_or_error(model_class, **kwargs):
    try:
        return model_class.objects.get(**kwargs)
    except model_class.DoesNotExist:
        return None


def error_response(message, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"detail": message}, status=http_status)


def list_objects(model_class, user, serializer_class):
    objects = model_class.objects.filter(user=user)
    serializer = serializer_class(objects, many=True)
    return Response(serializer.data)
