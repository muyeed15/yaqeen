from django.utils import timezone
from rest_framework import serializers

from cards.models import Card

CARD_NETWORKS = {"visa": "4", "mastercard": "5", "amex": "3", "nexus": "6"}


def _detect_network(digits):
    for network, prefix in CARD_NETWORKS.items():
        if digits.startswith(prefix):
            return network
    return ""


class CardSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(write_only=True, max_length=19)
    cardholder_name = serializers.CharField(
        required=False, allow_blank=True, max_length=100
    )
    card_network = serializers.CharField(required=False, max_length=12)

    class Meta:
        model = Card
        fields = [
            "id",
            "last_four",
            "masked_number",
            "cardholder_name",
            "card_network",
            "card_type",
            "card_number",
            "expiry_month",
            "expiry_year",
            "status",
            "created_at",
        ]
        read_only_fields = ["last_four", "masked_number", "status", "created_at"]

    def validate_card_number(self, value):
        digits = value.replace(" ", "")
        if not digits.isdigit():
            raise serializers.ValidationError("Card number must contain only digits.")
        if len(digits) < 13 or len(digits) > 19:
            raise serializers.ValidationError("Invalid card number length.")
        return digits

    def validate_card_network(self, value):
        if not value:
            return value
        digits = self.initial_data.get("card_number", "").replace(" ", "")
        expected = CARD_NETWORKS.get(value, "")
        if expected and digits[:1] != expected:
            raise serializers.ValidationError(
                f"Card number does not match {value} network."
            )
        return value

    def validate_expiry_month(self, value):
        if not (1 <= value <= 12):
            raise serializers.ValidationError("Expiry month must be between 1 and 12.")
        return value

    def validate_expiry_year(self, value):
        now = timezone.now()
        month = int(self.initial_data.get("expiry_month", 1))
        if value < now.year:
            raise serializers.ValidationError("Card is already expired.")
        if value == now.year and month < now.month:
            raise serializers.ValidationError("Card is already expired.")
        return value

    def create(self, validated_data):
        raw_number = validated_data.pop("card_number")
        network = validated_data.pop("card_network", "") or _detect_network(raw_number)
        validated_data["card_network"] = network
        card = Card(**validated_data)
        card.set_number(raw_number)
        card.save()
        return card
