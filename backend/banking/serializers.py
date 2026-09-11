from rest_framework import serializers

from .models import Bank, BankAccount, BankTransaction


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ["id", "name", "bank_code", "logo", "is_islamic", "is_active"]


class BankAccountSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source="bank.name", read_only=True)
    masked_account = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = [
            "id",
            "bank",
            "bank_name",
            "account_number",
            "masked_account",
            "account_holder",
            "branch",
            "routing_number",
            "is_primary",
            "is_verified",
            "created_at",
        ]
        read_only_fields = ["is_verified", "created_at"]

    def get_masked_account(self, obj):
        if len(obj.account_number) > 4:
            return "*" * (len(obj.account_number) - 4) + obj.account_number[-4:]
        return obj.account_number


class BankTransactionSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source="bank_account.bank.name", read_only=True)

    class Meta:
        model = BankTransaction
        fields = [
            "id",
            "bank_account",
            "bank_name",
            "amount",
            "fee",
            "transaction_type",
            "reference",
            "status",
            "created_at",
        ]
        read_only_fields = ["reference", "status", "created_at"]


class AddMoneySerializer(serializers.Serializer):
    bank_account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class WithdrawSerializer(serializers.Serializer):
    bank_account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
