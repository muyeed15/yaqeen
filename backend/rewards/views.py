import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page, get_page_size, paginate
from common.utils import error_response
from notifications.models import Notification

from .models import Offer, PointsTransaction, Reward, UserOffer
from .serializers import (
    OfferSerializer,
    PointsTransactionSerializer,
    RewardSerializer,
)

logger = logging.getLogger("rewards")


class RewardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reward, _ = Reward.objects.get_or_create(user=request.user)
        return Response(RewardSerializer(reward).data)


class PointsHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = PointsTransaction.objects.filter(user=request.user).order_by("-created_at")
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": PointsTransactionSerializer(p["queryset"], many=True).data,
            }
        )


class OfferListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        offers = Offer.objects.filter(
            is_active=True, valid_from__lte=now, valid_until__gte=now
        )
        return Response(OfferSerializer(offers, many=True).data)


class ClaimOfferView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            offer = Offer.objects.get(id=pk, is_active=True)
        except Offer.DoesNotExist:
            return error_response("Offer not found or inactive.", 404)

        if UserOffer.objects.filter(user=request.user, offer=offer).exists():
            return error_response("Offer already claimed.")

        reward, _ = Reward.objects.get_or_create(user=request.user)
        if reward.points < offer.points_required:
            return error_response(
                f"Not enough points. Required: {offer.points_required}, "
                f"You have: {reward.points}"
            )

        reward.points -= offer.points_required
        reward.save(update_fields=["points"])

        UserOffer.objects.create(
            user=request.user, offer=offer, is_claimed=True, claimed_at=timezone.now()
        )

        PointsTransaction.objects.create(
            user=request.user,
            points=offer.points_required,
            transaction_type="redeem",
            reason=f"Redeemed: {offer.title}",
        )

        Notification.objects.create(
            user=request.user,
            message=(
                f"You redeemed {offer.points_required} points for '{offer.title}'."
            ),
        )

        return Response({"message": f"Offer '{offer.title}' claimed successfully."})
