from rest_framework import serializers

from accounts.models import User
from transactions.models import MoneyRequest, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    sender_phone = serializers.CharField(
        source="sender.phone", read_only=True, allow_null=True
    )
    receiver_phone = serializers.CharField(
        source="receiver.phone", read_only=True, allow_null=True
    )
    merchant_name = serializers.CharField(
        source="merchant.business_name", read_only=True, allow_null=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "reference_id",
            "sender_phone",
            "receiver_phone",
            "merchant_name",
            "counterparty",
            "amount",
            "fee",
            "transaction_type",
            "status",
            "note",
            "created_at",
        ]
        read_only_fields = ["reference_id", "fee", "status", "created_at"]


class TransferSerializer(serializers.Serializer):
    receiver_phone = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_receiver_phone(self, value):
        if not User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "No account found with this phone number."
            )
        return value


class MoneyRequestSerializer(serializers.ModelSerializer):
    requester_phone = serializers.CharField(source="requester.phone", read_only=True)
    target_phone = serializers.CharField(source="target.phone", read_only=True)

    class Meta:
        model = MoneyRequest
        fields = [
            "id",
            "requester",
            "requester_phone",
            "target",
            "target_phone",
            "amount",
            "note",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]


class CreateMoneyRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_phone(self, value):
        if not User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "No account found with this phone number."
            )
        return value
