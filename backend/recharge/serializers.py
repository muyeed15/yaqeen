from rest_framework import serializers

from .models import DataPack, Operator, RechargeTransaction


class OperatorSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    type_label = serializers.SerializerMethodField()

    class Meta:
        model = Operator
        fields = ["id", "name", "operator_code", "logo", "type", "type_label", "is_active"]

    def get_logo(self, obj):
        if not obj.logo:
            return None
        return obj.logo.url

    def get_type(self, obj):
        return obj.type.key if obj.type_id else ""

    def get_type_label(self, obj):
        return obj.type.label if obj.type_id else ""


class DataPackSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source="operator.name", read_only=True)

    class Meta:
        model = DataPack
        fields = [
            "id",
            "operator",
            "operator_name",
            "name",
            "volume",
            "validity_days",
            "amount",
            "is_active",
        ]


class RechargeSerializer(serializers.Serializer):
    operator_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    recharge_type = serializers.ChoiceField(
        choices=[("prepaid", "Prepaid"), ("postpaid", "Postpaid"), ("data_pack", "Data Pack")]
    )
    data_pack_id = serializers.IntegerField(required=False)

    def validate_phone_number(self, value):
        digits = value.replace("+", "").replace(" ", "")
        if not digits.isdigit():
            raise serializers.ValidationError("Invalid phone number.")
        if len(digits) < 10 or len(digits) > 14:
            raise serializers.ValidationError("Phone number must be 10-14 digits.")
        return digits

    def validate_amount(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        if data["recharge_type"] in ("prepaid", "postpaid") and not data.get("amount"):
            raise serializers.ValidationError({"amount": "Amount is required."})
        if data["recharge_type"] == "data_pack" and not data.get("data_pack_id"):
            raise serializers.ValidationError({"data_pack_id": "Data pack is required."})
        return data


class RechargeTransactionSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source="operator.name", read_only=True)

    class Meta:
        model = RechargeTransaction
        fields = [
            "id",
            "operator",
            "operator_name",
            "phone_number",
            "amount",
            "fee",
            "recharge_type",
            "reference",
            "status",
            "created_at",
        ]
        read_only_fields = ["reference", "status", "created_at"]
