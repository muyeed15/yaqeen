from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from common.tests.helpers import make_merchant_category, make_user, make_wallet
from merchants.models import Merchant
from notifications.models import Notification
from transactions.models import Transaction


class MerchantListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)

    def test_list_only_verified_merchants(self):
        m_user1 = make_user("01700000002", "2222222222")
        Merchant.objects.create(
            user=m_user1,
            business_name="Verified Shop",
            category=make_merchant_category(),
            is_verified=True,
        )
        m_user2 = make_user("01700000003", "3333333333")
        Merchant.objects.create(
            user=m_user2,
            business_name="Unverified Shop",
            category=make_merchant_category(),
            is_verified=False,
        )
        res = self.client.get("/api/merchants/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["results"][0]["business_name"], "Verified Shop")

    def test_list_paginated(self):
        res = self.client.get("/api/merchants/")
        self.assertIn("count", res.data)
        self.assertIn("results", res.data)


class MerchantPayViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.payer = make_user("01700000001", "1111111111")
        make_wallet(self.payer, "1000.00")
        self.merchant_user = make_user("01700000002", "2222222222")
        self.merchant_wallet = make_wallet(self.merchant_user, "0.00")
        self.merchant = Merchant.objects.create(
            user=self.merchant_user,
            business_name="Shop",
            category=make_merchant_category(),
            is_verified=True,
        )
        self.client.force_authenticate(user=self.payer)

    def test_successful_payment(self):
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "100.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.merchant_wallet.refresh_from_db()
        self.assertEqual(self.merchant_wallet.balance, Decimal("100.00"))

    def test_payer_balance_deducted_with_fee(self):
        self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "100.00",
            },
        )
        wallet = self.payer.wallet
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("898.50"))

    def test_cannot_pay_own_merchant(self):
        Merchant.objects.create(
            user=self.payer,
            business_name="My Shop",
            category=make_merchant_category(),
            is_verified=True,
        )
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.payer.phone,
                "amount": "100.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_insufficient_balance(self):
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "99999.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unverified_merchant_rejected(self):
        Merchant.objects.create(
            user=make_user("01700000003", "3333333333"),
            business_name="Not Verified",
            category=make_merchant_category(),
            is_verified=False,
        )
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": "01700000003",
                "amount": "100.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_frozen_payer_wallet_rejected(self):
        wallet = self.payer.wallet
        wallet.status = "frozen"
        wallet.save()
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "100.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_amount_rejected(self):
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "0.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_notifications_created(self):
        self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "100.00",
            },
        )
        self.assertEqual(Notification.objects.filter(user=self.payer).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.merchant_user).count(), 1)

    def test_transaction_record_created(self):
        self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "100.00",
            },
        )
        self.assertEqual(Transaction.objects.count(), 1)
        tx = Transaction.objects.first()
        self.assertEqual(tx.transaction_type, "payment")
        self.assertEqual(tx.status, "completed")

    def test_pay_with_note(self):
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "50.00",
                "note": "Thanks for the service",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tx = Transaction.objects.first()
        self.assertIn("Thanks", tx.note)

    def test_pay_exact_balance(self):
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "985.22",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        wallet = self.payer.wallet
        wallet.refresh_from_db()
        self.assertAlmostEqual(float(wallet.balance), 0.0, places=2)

    def test_invalid_merchant_phone(self):
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": "01700000099",
                "amount": "100.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_frozen_merchant_wallet_rejected(self):
        self.merchant_wallet.status = "frozen"
        self.merchant_wallet.save()
        res = self.client.post(
            "/api/pay/merchant/",
            {
                "merchant_phone": self.merchant_user.phone,
                "amount": "100.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
