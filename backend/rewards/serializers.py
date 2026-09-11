from rest_framework import serializers

from .models import Offer, PointsTransaction, Reward


class RewardSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Reward
        fields = ["id", "user_phone", "points", "lifetime_points"]


class PointsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsTransaction
        fields = ["id", "points", "transaction_type", "reason", "created_at"]


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "description",
            "points_required",
            "cashback_amount",
            "cashback_pct",
            "category",
            "valid_from",
            "valid_until",
            "is_active",
        ]
