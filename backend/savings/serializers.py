from rest_framework import serializers

from .models import MudarabahAccount, MudarabahContribution, MudarabahPlan


class MudarabahPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MudarabahPlan
        fields = [
            "id",
            "name",
            "duration_months",
            "monthly_amount",
            "profit_ratio",
            "is_active",
        ]


class MudarabahAccountSerializer(serializers.ModelSerializer):
    plan_details = MudarabahPlanSerializer(source="plan", read_only=True)

    class Meta:
        model = MudarabahAccount
        fields = [
            "id",
            "account_number",
            "plan",
            "plan_details",
            "status",
            "start_date",
            "maturity_date",
            "total_deposited",
            "expected_payout",
            "created_at",
        ]
        read_only_fields = [
            "account_number",
            "total_deposited",
            "expected_payout",
            "created_at",
        ]


class MudarabahContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MudarabahContribution
        fields = [
            "id",
            "mudarabah_account",
            "installment_number",
            "amount",
            "status",
            "paid_at",
        ]
        read_only_fields = ["paid_at"]


class PayContributionSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
