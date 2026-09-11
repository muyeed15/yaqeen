from rest_framework import serializers

from .models import QardHasanApplication, QardHasanProduct


class QardHasanProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = QardHasanProduct
        fields = [
            "id",
            "name",
            "min_amount",
            "max_amount",
            "tenure_days",
            "service_fee",
            "description",
            "is_active",
        ]


class QardHasanApplicationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = QardHasanApplication
        fields = [
            "id",
            "loan_reference",
            "product",
            "product_name",
            "amount",
            "service_fee",
            "amount_due",
            "amount_paid",
            "hibah_given",
            "tenure_days",
            "status",
            "due_date",
            "disbursed_at",
            "created_at",
        ]
        read_only_fields = ["loan_reference", "status", "due_date", "disbursed_at", "created_at"]


class ApplyQardHasanSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class RepayQardHasanSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    hibah = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, default=0.00)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
