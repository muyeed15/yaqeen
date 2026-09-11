from decimal import Decimal

from django.test import TestCase

from accounts.models import CharityCause, Foundation, User, Wallet
from common.tests.helpers import make_cause


def make_user(phone, nid, full_name="Test User", password="testpass123"):
    return User.objects.create_user(phone=phone, password=password, full_name=full_name, nid=nid)


def make_wallet(user, balance="5000.00"):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.balance = Decimal(balance)
    wallet.save(update_fields=["balance"])
    return wallet


class UserModelTest(TestCase):
    def test_create_user(self):
        user = make_user("01700000001", "1234567890")
        self.assertEqual(str(user), "01700000001")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            phone="01700000002", password="pass", full_name="Admin", nid="9999999999"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_phone_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(phone="", password="pass", full_name="No Phone", nid="111")


class WalletModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.wallet = make_wallet(self.user)

    def test_str(self):
        self.assertIn("01700000001", str(self.wallet))

    def test_default_status_is_active(self):
        self.assertEqual(self.wallet.status, "active")

    def test_default_daily_limit(self):
        self.assertEqual(self.wallet.daily_limit, Decimal("10000.00"))


class FoundationModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.foundation = Foundation.objects.create(
            user=self.user,
            organization_name="Helping Hands",
            registration_number="REG-001",
            cause=make_cause("education"),
            contact_email="help@example.com",
            contact_phone="01700000002",
        )

    def test_str(self):
        self.assertEqual(str(self.foundation), "Helping Hands")

    def test_default_is_not_verified(self):
        self.assertFalse(self.foundation.is_verified)

    def test_registration_number_unique(self):
        with self.assertRaises(Exception):
            Foundation.objects.create(
                user=make_user("01700000003", "3333333333"),
                organization_name="Another",
                registration_number="REG-001",
                cause=make_cause("health"),
            )

    def test_cause_choices(self):
        valid_causes = list(CharityCause.objects.values_list("key", flat=True))
        self.assertIn(self.foundation.cause.key, valid_causes)

    def test_ordering(self):
        user2 = make_user("01700000002", "2222222222")
        f2 = Foundation.objects.create(
            user=user2,
            organization_name="A Fund",
            registration_number="REG-002",
            cause=make_cause("health"),
        )
        qs = Foundation.objects.all()
        self.assertEqual(qs.first(), f2)

    def test_all_cause_choices_valid(self):
        for i, (key, label, icon) in enumerate(
            [
                ("education", "Education", "GraduationCap"),
                ("health", "Health", "HeartPulse"),
                ("masjid", "Masjid Development", "Landmark"),
            ]
        ):
            cause = make_cause(key, label, icon)
            phone = f"0170000{i+1:0>2}99"
            nid = str(1000000000 + i)
            reg = f"REG-C{i}"
            f = Foundation.objects.create(
                user=make_user(phone, nid),
                organization_name=f"Fund {key}",
                registration_number=reg,
                cause=cause,
            )
            self.assertEqual(f.cause.key, key)

    def test_minimal_foundation(self):
        f = Foundation.objects.create(
            user=make_user("0170000099", "9999999999"),
            organization_name="Minimal",
            registration_number="REG-MIN",
            cause=make_cause("general"),
        )
        self.assertEqual(f.website, "")
        self.assertEqual(f.contact_email, "")
        self.assertEqual(f.contact_phone, "")
        self.assertEqual(f.description, "")
