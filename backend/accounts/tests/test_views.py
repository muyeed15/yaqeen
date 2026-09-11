from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Foundation
from agents.models import Agent
from common.tests.helpers import make_cause, make_merchant_category, make_user, make_wallet
from merchants.models import Merchant


class MeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)

    def test_get_me(self):
        res = self.client.get("/api/me/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["phone"], "01700000001")
        self.assertEqual(res.data["full_name"], "Test User")

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/me/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class WalletDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.wallet = make_wallet(self.user, "1000.00")
        self.client.force_authenticate(user=self.user)

    def test_get_wallet(self):
        res = self.client.get("/api/wallet/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user_phone"], "01700000001")
        self.assertEqual(res.data["balance"], "1000.00")
        self.assertEqual(res.data["status"], "active")

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/wallet/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class QRCodeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)

    def test_get_qr_code(self):
        res = self.client.get("/api/qr/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res["Content-Type"], "image/png")
        self.assertIn("qr-01700000001.png", res["Content-Disposition"])

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/qr/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class FoundationListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)

    def test_list_verified_foundations(self):
        user2 = make_user("01700000002", "2222222222")
        Foundation.objects.create(
            user=user2,
            organization_name="Charity One",
            registration_number="REG-001",
            cause=make_cause("education"),
            is_verified=True,
        )
        user3 = make_user("01700000003", "3333333333")
        Foundation.objects.create(
            user=user3,
            organization_name="Charity Two",
            registration_number="REG-002",
            cause=make_cause("health"),
            is_verified=False,
        )
        res = self.client.get("/api/foundations/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["organization_name"], "Charity One")


class FoundationDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)
        self.foundation_user = make_user("01700000002", "2222222222")
        self.foundation = Foundation.objects.create(
            user=self.foundation_user,
            organization_name="Help Fund",
            registration_number="REG-001",
            cause=make_cause("poverty"),
            is_verified=True,
        )

    def test_get_verified_foundation(self):
        res = self.client.get(f"/api/foundations/{self.foundation.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["organization_name"], "Help Fund")

    def test_get_unverified_foundation_returns_404(self):
        user3 = make_user("01700000003", "3333333333")
        f = Foundation.objects.create(
            user=user3,
            organization_name="Hidden",
            registration_number="REG-002",
            cause=make_cause("health"),
            is_verified=False,
        )
        res = self.client.get(f"/api/foundations/{f.pk}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_foundation(self):
        res = self.client.get("/api/foundations/9999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class WalletZeroBalanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.wallet = self.user.wallet
        self.wallet.balance = Decimal("0.00")
        self.wallet.save()
        self.client.force_authenticate(user=self.user)

    def test_zero_balance_wallet(self):
        res = self.client.get("/api/wallet/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["balance"], "0.00")


class PhoneLookupViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)

    def test_lookup_user_name(self):
        make_user("01700000002", "2222222222", full_name="Jane Doe")
        res = self.client.get("/api/lookup/01700000002/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Jane Doe")
        self.assertEqual(res.data["full_name"], "Jane Doe")
        self.assertEqual(res.data["type"], "user")
        self.assertFalse(res.data["is_verified_merchant"])

    def test_lookup_verified_merchant_name(self):
        m_user = make_user("01700000002", "2222222222", full_name="Ali Ahmed")
        Merchant.objects.create(
            user=m_user,
            business_name="Aarong",
            category=make_merchant_category(),
            is_verified=True,
        )
        res = self.client.get("/api/lookup/01700000002/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Aarong")
        self.assertEqual(res.data["full_name"], "Ali Ahmed")
        self.assertEqual(res.data["type"], "merchant")
        self.assertTrue(res.data["is_verified_merchant"])

    def test_lookup_unverified_merchant_falls_back_to_user_name(self):
        m_user = make_user("01700000002", "2222222222", full_name="Ali")
        Merchant.objects.create(
            user=m_user,
            business_name="Hidden Shop",
            category=make_merchant_category(),
            is_verified=False,
        )
        res = self.client.get("/api/lookup/01700000002/")
        self.assertEqual(res.data["name"], "Ali")
        self.assertEqual(res.data["full_name"], "Ali")
        self.assertEqual(res.data["type"], "user")
        self.assertFalse(res.data["is_verified_merchant"])

    def test_lookup_agent_name(self):
        Agent.objects.create(
            full_name="Rahim Uddin",
            phone="01700000003",
            nid="3333333333",
            shop_name="Rahim General Store",
            district="Dhaka",
            thana="Mirpur",
            address="Mirpur 10",
            is_verified=True,
            status="active",
        )
        res = self.client.get("/api/lookup/01700000003/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Rahim General Store")
        self.assertEqual(res.data["full_name"], "Rahim Uddin")
        self.assertEqual(res.data["type"], "agent")

    def test_lookup_unknown_phone(self):
        res = self.client.get("/api/lookup/01700000999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/lookup/01700000002/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
