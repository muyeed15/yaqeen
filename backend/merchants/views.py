import logging
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Wallet
from common.pagination import get_page, get_page_size, paginate
from common.utils import daily_spent, error_response
from merchants.models import Merchant
from merchants.serializers import MerchantPaySerializer, MerchantSerializer
from notifications.models import Notification
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer

logger = logging.getLogger("merchants")


class MerchantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            Merchant.verified.select_related("user", "category")
            .only(
                "id",
                "business_name",
                "category",
                "is_verified",
                "user__phone",
                "category__key",
                "category__label",
            )
            .order_by("business_name")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": MerchantSerializer(p["queryset"], many=True).data,
            }
        )


class MerchantPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MerchantPaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        merchant = serializer.validated_data["merchant"]
        amount = serializer.validated_data["amount"]
        note = serializer.validated_data["note"]

        if merchant.user == request.user:
            return error_response("Cannot pay your own merchant account.")

        fee_rate = Decimal(str(settings.TRANSFER_FEE_PERCENT)) / Decimal("100")
        fee = (amount * fee_rate).quantize(Decimal("0.01"))
        total_debit = amount + fee

        try:
            with transaction.atomic():
                sender_wallet = Wallet.objects.select_for_update().get(user=request.user)
                try:
                    merchant_wallet = Wallet.objects.select_for_update().get(user=merchant.user)
                except ObjectDoesNotExist:
                    raise ValueError("Merchant wallet is unavailable.")

                if sender_wallet.status != "active":
                    raise ValueError("Your wallet is frozen.")
                if merchant_wallet.status != "active":
                    raise ValueError("Merchant wallet is unavailable.")
                if sender_wallet.balance < total_debit:
                    raise ValueError(
                        f"Insufficient balance. Required: ৳{total_debit} "
                        f"(৳{amount} + ৳{fee} fee)."
                    )

                today = timezone.now().date()
                spent_today = daily_spent(request.user, today)
                if spent_today + total_debit > sender_wallet.daily_limit:
                    remaining = max(sender_wallet.daily_limit - spent_today, Decimal("0"))
                    raise ValueError(f"Daily limit exceeded. Remaining today: ৳{remaining}.")

                sender_wallet.balance -= total_debit
                merchant_wallet.balance += amount
                sender_wallet.save(update_fields=["balance"])
                merchant_wallet.save(update_fields=["balance"])

                tx = Transaction.objects.create(
                    sender=request.user,
                    receiver=merchant.user,
                    merchant=merchant,
                    amount=amount,
                    fee=fee,
                    transaction_type="payment",
                    status="completed",
                    note=note or f"Payment to {merchant.business_name}",
                )

                Notification.objects.bulk_create(
                    [
                        Notification(
                            user=request.user,
                            message=(
                                f"You paid ৳{amount} to {merchant.business_name}. "
                                f"Fee: ৳{fee}. Ref: {tx.reference_id}"
                            ),
                        ),
                        Notification(
                            user=merchant.user,
                            message=(
                                f"Payment of ৳{amount} received from {request.user.phone} "
                                f"at {merchant.business_name}. Ref: {tx.reference_id}"
                            ),
                        ),
                    ]
                )

        except (ValueError, ObjectDoesNotExist) as e:
            logger.warning(
                "MerchantPayView: %s, user=%s merchant=%s amount=%s",
                e,
                request.user.phone,
                merchant.business_name,
                amount,
            )
            return error_response(str(e))

        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
