from rest_framework import serializers

from .models import RemittancePartner, RemittanceTransaction


class RemittancePartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemittancePartner
        fields = [
            "id",
            "name",
            "country",
            "currency",
            "exchange_rate",
            "logo",
            "is_active",
        ]


class RemittanceTransactionSerializer(serializers.ModelSerializer):
    partner_name = serializers.CharField(source="partner.name", read_only=True)
    partner_country = serializers.CharField(source="partner.country", read_only=True)

    class Meta:
        model = RemittanceTransaction
        fields = [
            "id",
            "partner",
            "partner_name",
            "partner_country",
            "sender_name",
            "sender_country",
            "amount_foreign",
            "amount_bdt",
            "exchange_rate",
            "reference_number",
            "status",
            "created_at",
        ]
        read_only_fields = ["reference_number", "status", "created_at"]


class ReceiveRemittanceSerializer(serializers.Serializer):
    partner_id = serializers.IntegerField()
    sender_name = serializers.CharField(max_length=100)
    sender_country = serializers.CharField(max_length=50)
    amount_foreign = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount_foreign(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
