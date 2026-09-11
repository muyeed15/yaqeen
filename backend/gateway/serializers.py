from rest_framework import serializers

from .models import GatewayTransaction


class GatewayTransactionSerializer(serializers.ModelSerializer):
    merchant_name = serializers.CharField(
        source="gateway.merchant.business_name", read_only=True
    )

    class Meta:
        model = GatewayTransaction
        fields = [
            "id",
            "txn_id",
            "gateway",
            "merchant_name",
            "amount",
            "fee",
            "order_id",
            "status",
            "created_at",
        ]
        read_only_fields = ["txn_id", "status", "created_at"]
