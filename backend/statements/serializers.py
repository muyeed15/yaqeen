from rest_framework import serializers

from .models import AccountStatement


class StatementSerializer(serializers.ModelSerializer):
    period = serializers.SerializerMethodField()

    class Meta:
        model = AccountStatement
        fields = [
            "id",
            "year",
            "month",
            "period",
            "opening_balance",
            "closing_balance",
            "total_credits",
            "total_debits",
            "transaction_count",
            "generated_at",
        ]

    def get_period(self, obj):
        from calendar import month_name

        return f"{month_name[obj.month]} {obj.year}"


class GenerateStatementSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField(min_value=1, max_value=12)
