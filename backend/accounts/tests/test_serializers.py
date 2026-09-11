from django.test import TestCase

from accounts.models import Foundation
from accounts.serializers import FoundationSerializer, UserSerializer, WalletSerializer
from common.tests.helpers import make_cause, make_merchant_category, make_user, make_wallet


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")

    def test_serializer_contains_expected_fields(self):
        serializer = UserSerializer(self.user)
        expected = {
            "id",
            "phone",
            "full_name",
            "nid",
            "role",
            "is_verified",
            "is_active",
            "has_merchant_profile",
            "created_at",
        }
        self.assertEqual(set(serializer.data.keys()), expected)

    def test_has_merchant_profile_false(self):
        serializer = UserSerializer(self.user)
        self.assertFalse(serializer.data["has_merchant_profile"])

    def test_read_only_fields(self):
        serializer = UserSerializer(self.user)
        self.assertIn("role", serializer.data)

    def test_merchant_profile_true(self):
        from merchants.models import Merchant

        Merchant.objects.create(
            user=self.user,
            business_name="Shop",
            category=make_merchant_category(),
        )
        serializer = UserSerializer(self.user)
        self.assertTrue(serializer.data["has_merchant_profile"])


class WalletSerializerTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.wallet = make_wallet(self.user, "2500.00")

    def test_serializer_contains_expected_fields(self):
        serializer = WalletSerializer(self.wallet)
        expected = {"id", "user_phone", "balance", "daily_limit", "status", "created_at"}
        self.assertEqual(set(serializer.data.keys()), expected)

    def test_user_phone(self):
        serializer = WalletSerializer(self.wallet)
        self.assertEqual(serializer.data["user_phone"], "01700000001")

    def test_balance_read_only(self):
        serializer = WalletSerializer(self.wallet)
        self.assertIn("balance", serializer.data)


class FoundationSerializerTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.foundation = Foundation.objects.create(
            user=self.user,
            organization_name="Good Cause",
            registration_number="REG-001",
            cause=make_cause("education"),
        )

    def test_serializer_contains_expected_fields(self):
        serializer = FoundationSerializer(self.foundation)
        expected = {
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
        }
        self.assertEqual(set(serializer.data.keys()), expected)

    def test_logo_none_without_request(self):
        serializer = FoundationSerializer(self.foundation)
        self.assertIsNone(serializer.data["logo"])

    def test_phone_source(self):
        serializer = FoundationSerializer(self.foundation)
        self.assertEqual(serializer.data["phone"], "01700000001")

    def test_is_verified_read_only(self):
        serializer = FoundationSerializer(self.foundation)
        self.assertFalse(serializer.data["is_verified"])
