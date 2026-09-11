from decimal import Decimal

from django.test import TestCase

from charity.models import HawlTracking, Sadaqah, SadaqahJariyah, ZakatPayment
from common.tests.helpers import make_cause, make_user


class ZakatPaymentModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.payment = ZakatPayment.objects.create(
            user=self.user,
            amount=Decimal("250.00"),
        )

    def test_str(self):
        self.assertIn("Zakat", str(self.payment))
        self.assertIn(self.user.phone, str(self.payment))

    def test_default_asset_type_none(self):
        self.assertIsNone(self.payment.asset_type)

    def test_recipient_optional(self):
        self.assertIsNone(self.payment.recipient)

    def test_zakat_with_all_fields(self):
        recipient = make_user("0170000099", "9999999999")
        payment = ZakatPayment.objects.create(
            user=self.user,
            recipient=recipient,
            amount=Decimal("500.00"),
            asset_type="gold",
            hawl_year=1446,
        )
        self.assertEqual(payment.asset_type, "gold")
        self.assertEqual(payment.hawl_year, 1446)
        self.assertIsNotNone(payment.paid_at)


class SadaqahModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.donation = Sadaqah.objects.create(
            user=self.user,
            amount=Decimal("50.00"),
        )

    def test_str(self):
        self.assertIn("Sadaqah", str(self.donation))

    def test_default_anonymous_false(self):
        self.assertFalse(self.donation.is_anonymous)


class HawlTrackingModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.hawl = HawlTracking.objects.create(user=self.user)

    def test_str(self):
        self.assertIn(self.user.phone, str(self.hawl))

    def test_default_not_eligible(self):
        self.assertFalse(self.hawl.is_eligible)

    def test_hawl_str_with_none_dates(self):
        self.assertIn("None", str(self.hawl))


class SadaqahJariyahModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.sj = SadaqahJariyah.objects.create(
            user=self.user,
            amount=Decimal("100.00"),
            cause=make_cause("water"),
        )

    def test_str(self):
        self.assertIn("SJ", str(self.sj))

    def test_default_frequency_monthly(self):
        self.assertEqual(self.sj.frequency, "monthly")

    def test_default_is_active(self):
        self.assertTrue(self.sj.is_active)

    def test_next_due_date_set_on_save(self):
        self.assertIsNotNone(self.sj.next_due_date)

    def test_total_donated_defaults_zero(self):
        sj2 = SadaqahJariyah.objects.create(
            user=self.user,
            amount=Decimal("100.00"),
        )
        self.assertEqual(sj2.total_donated, Decimal("0.00"))
