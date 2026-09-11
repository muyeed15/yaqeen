from rest_framework import serializers

from accounts.models import Foundation, KYCVerification, Nominee, User, Wallet


class UserSerializer(serializers.ModelSerializer):
    has_merchant_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "full_name",
            "nid",
            "role",
            "is_verified",
            "is_active",
            "has_merchant_profile",
            "created_at",
        ]
        read_only_fields = ["role", "is_verified", "is_active", "created_at"]

    def get_has_merchant_profile(self, obj):
        return hasattr(obj, "merchant_profile")


class WalletSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "user_phone", "balance", "daily_limit", "status", "created_at"]
        read_only_fields = ["balance", "created_at"]


class NomineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nominee
        fields = [
            "id",
            "full_name",
            "phone",
            "nid",
            "relationship",
            "is_primary",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class KYCVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        fields = [
            "id",
            "document_type",
            "document_number",
            "date_of_birth",
            "address",
            "face_image",
            "status",
            "verified_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "verified_at", "created_at", "updated_at"]


class FoundationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="user.phone", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    logo = serializers.SerializerMethodField()
    cause = serializers.SerializerMethodField()
    cause_label = serializers.SerializerMethodField()
    cause_icon = serializers.SerializerMethodField()

    class Meta:
        model = Foundation
        fields = [
            "id",
            "organization_name",
            "cause",
            "cause_label",
            "cause_icon",
            "logo",
            "description",
            "website",
            "contact_email",
            "contact_phone",
            "is_verified",
            "phone",
            "user_id",
            "created_at",
        ]
        read_only_fields = ["is_verified", "created_at"]

    def get_logo(self, obj):
        if not obj.logo:
            return None
        return obj.logo.url

    def get_cause(self, obj):
        return obj.cause.key if obj.cause_id else ""

    def get_cause_label(self, obj):
        return obj.cause.label if obj.cause_id else ""

    def get_cause_icon(self, obj):
        return obj.cause.icon if obj.cause_id else "Heart"
