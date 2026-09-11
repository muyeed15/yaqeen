from rest_framework import serializers

from merchants.models import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="user.phone", read_only=True)
    category = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        fields = [
            "id",
            "business_name",
            "category",
            "category_label",
            "is_verified",
            "phone",
        ]
        read_only_fields = ["is_verified"]

    def get_category(self, obj):
        return obj.category.key if obj.category_id else ""

    def get_category_label(self, obj):
        return obj.category.label if obj.category_id else ""


class MerchantPaySerializer(serializers.Serializer):
    merchant_phone = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        try:
            merchant = Merchant.objects.select_related("user").get(
                user__phone=data["merchant_phone"], is_verified=True
            )
        except Merchant.DoesNotExist:
            raise serializers.ValidationError(
                {"merchant_phone": "No verified merchant found with this phone number."}
            )
        data["merchant"] = merchant
        return data
