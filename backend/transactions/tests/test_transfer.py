from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, Wallet
from notifications.models import Notification
from transactions.models import Transaction


def make_user(phone, nid, full_name="Test User", password="testpass123"):
    return User.objects.create_user(phone=phone, password=password, full_name=full_name, nid=nid)


def make_wallet(user, balance="5000.00"):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.balance = Decimal(balance)
    wallet.save(update_fields=["balance"])
    return wallet


class TransferViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.sender = make_user("01700000001", "1111111111", full_name="Sender")
        self.receiver = make_user("01700000002", "2222222222", full_name="Receiver")
        self.sender_wallet = make_wallet(self.sender, "5000.00")
        self.receiver_wallet = make_wallet(self.receiver, "0.00")
        self.client.force_authenticate(user=self.sender)

    def test_successful_transfer(self):
        res = self.client.post(
            "/api/transfer/", {"receiver_phone": "01700000002", "amount": "100.00"}
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.receiver_wallet.refresh_from_db()
        self.assertEqual(self.receiver_wallet.balance, Decimal("100.00"))

    def test_sender_balance_reduced_by_amount_plus_fee(self):
        self.client.post("/api/transfer/", {"receiver_phone": "01700000002", "amount": "100.00"})
        self.sender_wallet.refresh_from_db()
        self.assertEqual(self.sender_wallet.balance, Decimal("4898.50"))

    def test_self_transfer_rejected(self):
        res = self.client.post(
            "/api/transfer/", {"receiver_phone": "01700000001", "amount": "100.00"}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_insufficient_balance_rejected(self):
        res = self.client.post(
            "/api/transfer/", {"receiver_phone": "01700000002", "amount": "99999.00"}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_receiver_rejected(self):
        res = self.client.post(
            "/api/transfer/", {"receiver_phone": "01999999999", "amount": "100.00"}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_amount_rejected(self):
        res = self.client.post(
            "/api/transfer/", {"receiver_phone": "01700000002", "amount": "0.00"}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request_rejected(self):
        self.client.force_authenticate(user=None)
        res = self.client.post(
            "/api/transfer/", {"receiver_phone": "01700000002", "amount": "100.00"}
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_frozen_sender_wallet_rejected(self):
        self.sender_wallet.status = "frozen"
        self.sender_wallet.save()
        res = self.client.post(
            "/api/transfer/", {"receiver_phone": "01700000002", "amount": "100.00"}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_notifications_created_on_transfer(self):
        self.client.post("/api/transfer/", {"receiver_phone": "01700000002", "amount": "100.00"})
        self.assertEqual(Notification.objects.filter(user=self.sender).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.receiver).count(), 1)

    def test_transaction_record_created(self):
        self.client.post("/api/transfer/", {"receiver_phone": "01700000002", "amount": "100.00"})
        self.assertEqual(Transaction.objects.count(), 1)
        tx = Transaction.objects.first()
        self.assertEqual(tx.transaction_type, "send")
        self.assertEqual(tx.status, "completed")
