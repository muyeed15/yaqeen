from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from common.tests.helpers import make_user
from transactions.models import Transaction


class TransactionListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.sender = make_user("01700000001", "1111111111")
        self.receiver = make_user("01700000002", "2222222222")
        self.client.force_authenticate(user=self.sender)
        Transaction.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal("50.00"),
            transaction_type="send",
            status="completed",
        )

    def test_list_transactions(self):
        res = self.client.get("/api/transactions/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_list_returns_paginated_response(self):
        res = self.client.get("/api/transactions/")
        self.assertIn("count", res.data)
        self.assertIn("results", res.data)
        self.assertIn("page", res.data)
        self.assertIn("total_pages", res.data)

    def test_list_includes_received_transactions(self):
        self.client.force_authenticate(user=self.receiver)
        res = self.client.get("/api/transactions/")
        self.assertEqual(res.data["count"], 1)

    def test_list_excludes_other_users_transactions(self):
        other = make_user("01700000003", "3333333333")
        self.client.force_authenticate(user=other)
        res = self.client.get("/api/transactions/")
        self.assertEqual(res.data["count"], 0)

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/transactions/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TransactionDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.sender = make_user("01700000001", "1111111111")
        self.receiver = make_user("01700000002", "2222222222")
        self.tx = Transaction.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal("75.00"),
            transaction_type="send",
            status="completed",
        )
        self.client.force_authenticate(user=self.sender)

    def test_get_detail(self):
        res = self.client.get(f"/api/transactions/{self.tx.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["amount"], "75.00")

    def test_sender_can_view(self):
        res = self.client.get(f"/api/transactions/{self.tx.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_receiver_can_view(self):
        self.client.force_authenticate(user=self.receiver)
        res = self.client.get(f"/api/transactions/{self.tx.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_view(self):
        other = make_user("01700000003", "3333333333")
        self.client.force_authenticate(user=other)
        res = self.client.get(f"/api/transactions/{self.tx.pk}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent(self):
        res = self.client.get("/api/transactions/9999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class TransactionPaginationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        receiver = make_user("01700000002", "2222222222")
        for i in range(15):
            Transaction.objects.create(
                sender=self.user,
                receiver=receiver,
                amount=Decimal(f"{i+1}0.00"),
                transaction_type="send",
                status="completed",
            )
        self.client.force_authenticate(user=self.user)

    def test_default_page_size(self):
        res = self.client.get("/api/transactions/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 15)
        self.assertEqual(len(res.data["results"]), 10)

    def test_page_size_parameter(self):
        res = self.client.get("/api/transactions/?page_size=5")
        self.assertEqual(len(res.data["results"]), 5)

    def test_page_two(self):
        res = self.client.get("/api/transactions/?page=2&page_size=10")
        self.assertEqual(len(res.data["results"]), 5)
