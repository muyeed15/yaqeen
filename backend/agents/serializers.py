from rest_framework import serializers

from .models import Agent, AgentTransaction


class AgentSerializer(serializers.ModelSerializer):
    distance_km = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True, default=None
    )

    class Meta:
        model = Agent
        fields = [
            "id",
            "full_name",
            "phone",
            "shop_name",
            "district",
            "thana",
            "address",
            "latitude",
            "longitude",
            "distance_km",
            "is_verified",
            "status",
            "created_at",
        ]


class CashInOutSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    otp = serializers.CharField(max_length=6, required=False, allow_blank=True, default="")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class AgentTransactionSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source="user.phone", read_only=True)
    agent_name = serializers.CharField(source="agent.shop_name", read_only=True)

    class Meta:
        model = AgentTransaction
        fields = [
            "id",
            "user_phone",
            "agent_name",
            "amount",
            "fee",
            "commission",
            "transaction_type",
            "reference",
            "status",
            "created_at",
        ]
        read_only_fields = ["reference", "status", "created_at"]
