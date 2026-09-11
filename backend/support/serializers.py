from rest_framework import serializers

from .models import SupportCategory, SupportTicket, TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_phone = serializers.CharField(source="sender.phone", read_only=True)

    class Meta:
        model = TicketMessage
        fields = [
            "id",
            "sender",
            "sender_phone",
            "message",
            "is_staff_reply",
            "created_at",
        ]


class SupportTicketSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)
    category = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "user_phone",
            "subject",
            "category",
            "category_label",
            "status",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def get_category(self, obj):
        return obj.category.key if obj.category_id else ""

    def get_category_label(self, obj):
        return obj.category.label if obj.category_id else ""


class CreateTicketSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=30, required=False, allow_blank=True)
    message = serializers.CharField()

    def validate_category(self, value):
        if value and not SupportCategory.objects.filter(key=value).exists():
            raise serializers.ValidationError("Invalid category.")
        return value


class TicketReplySerializer(serializers.Serializer):
    message = serializers.CharField()
