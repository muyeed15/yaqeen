from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from charity.models import HawlTracking, Sadaqah, SadaqahJariyah, ZakatPayment
from common.tests.helpers import make_cause, make_user, make_wallet


class CalculateZakatTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)

    def test_wealth_above_nisab(self):
        res = self.client.post(
            "/api/zakat/calculate/",
            {
                "total_wealth": "100000.00",
                "nisab_threshold": "85000.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_eligible"])
        self.assertEqual(res.data["zakat_due"], "2500.00")

    def test_wealth_below_nisab(self):
        res = self.client.post(
            "/api/zakat/calculate/",
            {
                "total_wealth": "1000.00",
                "nisab_threshold": "85000.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["is_eligible"])
        self.assertEqual(res.data["zakat_due"], "0.00")

    def test_exact_nisab(self):
        res = self.client.post(
            "/api/zakat/calculate/",
            {
                "total_wealth": "85000.00",
                "nisab_threshold": "85000.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_eligible"])

    def test_default_nisab_used(self):
        res = self.client.post(
            "/api/zakat/calculate/",
            {
                "total_wealth": "200000.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["zakat_due"], "5000.00")

    def test_zero_wealth(self):
        res = self.client.post(
            "/api/zakat/calculate/",
            {
                "total_wealth": "0.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["is_eligible"])
        self.assertEqual(res.data["zakat_due"], "0.00")

    def test_very_large_wealth(self):
        res = self.client.post(
            "/api/zakat/calculate/",
            {
                "total_wealth": "999999999.99",
                "nisab_threshold": "85000.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_eligible"])
        self.assertEqual(res.data["zakat_due"], "25000000.00")


class PayZakatTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        make_wallet(self.user, "10000.00")
        self.foundation_user = make_user("01700000002", "2222222222")
        from accounts.models import Foundation

        self.foundation = Foundation.objects.create(
            user=self.foundation_user,
            organization_name="Zakat Fund",
            registration_number="REG-001",
            cause=make_cause("poverty"),
            is_verified=True,
        )
        make_wallet(self.foundation_user, "0.00")
        self.client.force_authenticate(user=self.user)

    def test_pay_zakat_success(self):
        res = self.client.post(
            "/api/zakat/pay/",
            {
                "amount": "500.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ZakatPayment.objects.count(), 1)

    def test_pay_zakat_deducts_sender(self):
        self.client.post(
            "/api/zakat/pay/",
            {
                "amount": "500.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        wallet = self.user.wallet
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("9500.00"))

    def test_pay_zakat_credits_foundation(self):
        self.client.post(
            "/api/zakat/pay/",
            {
                "amount": "500.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        f_wallet = self.foundation_user.wallet
        f_wallet.refresh_from_db()
        self.assertEqual(f_wallet.balance, Decimal("500.00"))

    def test_insufficient_balance(self):
        res = self.client.post(
            "/api/zakat/pay/",
            {
                "amount": "99999.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unverified_foundation_rejected(self):
        unverified_user = make_user("01700000003", "3333333333")
        from accounts.models import Foundation

        Foundation.objects.create(
            user=unverified_user,
            organization_name="Fake",
            registration_number="REG-002",
            cause=make_cause("general"),
            is_verified=False,
        )
        res = self.client.post(
            "/api/zakat/pay/",
            {
                "amount": "100.00",
                "recipient_id": unverified_user.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ZakatHistoryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        ZakatPayment.objects.create(user=self.user, amount=Decimal("100.00"))
        ZakatPayment.objects.create(user=self.user, amount=Decimal("200.00"))
        self.client.force_authenticate(user=self.user)

    def test_list_zakat_payments(self):
        res = self.client.get("/api/zakat/history/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)


class GiveSadaqahTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        make_wallet(self.user, "5000.00")
        self.foundation_user = make_user("01700000002", "2222222222")
        from accounts.models import Foundation

        Foundation.objects.create(
            user=self.foundation_user,
            organization_name="Sadaqah Fund",
            registration_number="REG-001",
            cause=make_cause("education"),
            is_verified=True,
        )
        make_wallet(self.foundation_user, "0.00")
        self.client.force_authenticate(user=self.user)

    def test_give_sadaqah_success(self):
        res = self.client.post(
            "/api/sadaqah/",
            {
                "amount": "100.00",
                "recipient_id": self.foundation_user.pk,
                "cause": "education",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sadaqah.objects.count(), 1)

    def test_give_anonymous_sadaqah(self):
        res = self.client.post(
            "/api/sadaqah/",
            {
                "amount": "100.00",
                "recipient_id": self.foundation_user.pk,
                "is_anonymous": True,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data["is_anonymous"])

    def test_give_sadaqah_without_cause(self):
        res = self.client.post(
            "/api/sadaqah/",
            {
                "amount": "50.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data.get("cause"))

    def test_give_sadaqah_invalid_cause(self):
        res = self.client.post(
            "/api/sadaqah/",
            {
                "amount": "50.00",
                "recipient_id": self.foundation_user.pk,
                "cause": "not_a_real_cause",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_give_sadaqah_exact_balance(self):
        wallet = self.user.wallet
        wallet.balance = Decimal("100.00")
        wallet.save()
        res = self.client.post(
            "/api/sadaqah/",
            {
                "amount": "100.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_insufficient_balance(self):
        res = self.client.post(
            "/api/sadaqah/",
            {
                "amount": "99999.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class SadaqahHistoryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        Sadaqah.objects.create(user=self.user, amount=Decimal("50.00"))
        self.client.force_authenticate(user=self.user)

    def test_list_sadaqah(self):
        res = self.client.get("/api/sadaqah/history/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)


class HawlTrackingViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)

    def test_get_hawl_creates_if_not_exists(self):
        res = self.client.get("/api/hawl/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(HawlTracking.objects.filter(user=self.user).exists())
        self.assertFalse(res.data["is_eligible"])

    def test_post_wealth_above_nisab(self):
        res = self.client.post("/api/hawl/", {"current_wealth": "100000.00"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_eligible"])
        self.assertIsNotNone(res.data["next_hawl_date"])

    def test_post_wealth_below_nisab(self):
        HawlTracking.objects.create(user=self.user, is_eligible=True)
        res = self.client.post("/api/hawl/", {"current_wealth": "1000.00"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["is_eligible"])

    def test_post_wealth_exactly_at_nisab(self):
        res = self.client.post("/api/hawl/", {"current_wealth": "85000.00"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_eligible"])
        self.assertIsNotNone(res.data["next_hawl_date"])

    def test_post_wealth_zero(self):
        res = self.client.post("/api/hawl/", {"current_wealth": "0.00"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["is_eligible"])

    def test_put_hawl_not_yet_due(self):
        res = self.client.put("/api/hawl/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "Hawl period not yet completed.")

    def test_put_hawl_due_renews(self):
        from datetime import date

        hawl = HawlTracking.objects.create(
            user=self.user,
            is_eligible=True,
            next_hawl_date=date.today(),
        )
        res = self.client.put("/api/hawl/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "Hawl renewed. Zakat is due.")
        hawl.refresh_from_db()
        self.assertIsNotNone(hawl.next_hawl_date)


class SadaqahJariyahListCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        make_wallet(self.user, "5000.00")
        self.foundation_user = make_user("01700000002", "2222222222")
        from accounts.models import Foundation

        Foundation.objects.create(
            user=self.foundation_user,
            organization_name="Jariyah Fund",
            registration_number="REG-001",
            cause=make_cause("water"),
            is_verified=True,
        )
        make_wallet(self.foundation_user, "0.00")
        self.client.force_authenticate(user=self.user)

    def test_list_empty(self):
        res = self.client.get("/api/sadaqah-jariyah/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_create_success(self):
        res = self.client.post(
            "/api/sadaqah-jariyah/",
            {
                "amount": "200.00",
                "recipient_id": self.foundation_user.pk,
                "cause": "water",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SadaqahJariyah.objects.count(), 1)
        self.assertEqual(res.data["total_donated"], "200.00")
        self.assertEqual(res.data["cause"], "water")
        self.assertEqual(res.data["cause_label"], "Water")

    def test_create_insufficient_balance(self):
        res = self.client.post(
            "/api/sadaqah-jariyah/",
            {
                "amount": "99999.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_without_cause(self):
        res = self.client.post(
            "/api/sadaqah-jariyah/",
            {
                "amount": "100.00",
                "recipient_id": self.foundation_user.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SadaqahJariyah.objects.count(), 1)

    def test_create_exact_balance(self):
        wallet = self.user.wallet
        wallet.balance = Decimal("200.00")
        wallet.save()
        res = self.client.post(
            "/api/sadaqah-jariyah/",
            {
                "amount": "200.00",
                "recipient_id": self.foundation_user.pk,
                "cause": "water",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("0.00"))


class SadaqahJariyahDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.sj = SadaqahJariyah.objects.create(
            user=self.user,
            amount=Decimal("100.00"),
            cause=make_cause("well"),
        )
        self.client.force_authenticate(user=self.user)

    def test_get_detail(self):
        res = self.client.get(f"/api/sadaqah-jariyah/{self.sj.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["cause"], "well")

    def test_patch_deactivate(self):
        res = self.client.patch(
            f"/api/sadaqah-jariyah/{self.sj.pk}/",
            {
                "is_active": False,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.sj.refresh_from_db()
        self.assertFalse(self.sj.is_active)

    def test_get_other_users_donation(self):
        other = make_user("01700000002", "2222222222")
        other_sj = SadaqahJariyah.objects.create(
            user=other,
            amount=Decimal("50.00"),
        )
        res = self.client.get(f"/api/sadaqah-jariyah/{other_sj.pk}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent(self):
        res = self.client.get("/api/sadaqah-jariyah/9999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_no_field_returns_error(self):
        res = self.client.patch(f"/api/sadaqah-jariyah/{self.sj.pk}/", {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_reactivate(self):
        self.sj.is_active = False
        self.sj.save()
        res = self.client.patch(
            f"/api/sadaqah-jariyah/{self.sj.pk}/",
            {
                "is_active": True,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.sj.refresh_from_db()
        self.assertTrue(self.sj.is_active)
