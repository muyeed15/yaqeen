from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from cards.models import Card
from common.tests.helpers import make_user, make_wallet


class CardListCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        make_wallet(self.user, "5000.00")
        self.client.force_authenticate(user=self.user)

    def test_list_cards_empty(self):
        res = self.client.get("/api/cards/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 0)

    def test_list_cards(self):
        Card.objects.create(
            user=self.user,
            last_four="1234",
            card_type="debit",
            expiry_month=12,
            expiry_year=2030,
        )
        res = self.client.get("/api/cards/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)

    def test_list_only_own_cards(self):
        other = make_user("01700000002", "2222222222")
        Card.objects.create(
            user=other,
            last_four="9999",
            card_type="prepaid",
            expiry_month=6,
            expiry_year=2029,
        )
        res = self.client.get("/api/cards/")
        self.assertEqual(res.data["count"], 0)

    def test_create_card_success(self):
        res = self.client.post(
            "/api/cards/",
            {
                "card_number": "4242424242424321",
                "card_type": "debit",
                "expiry_month": 12,
                "expiry_year": 2030,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["last_four"], "4321")
        self.assertEqual(res.data["card_network"], "visa")
        self.assertEqual(Card.objects.count(), 1)

    def test_create_card_invalid_number(self):
        res = self.client.post(
            "/api/cards/",
            {
                "card_number": "abc",
                "card_type": "debit",
                "expiry_month": 12,
                "expiry_year": 2030,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_card_expired_year(self):
        res = self.client.post(
            "/api/cards/",
            {
                "card_number": "4242424242424242",
                "card_type": "debit",
                "expiry_month": 12,
                "expiry_year": 2020,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/cards/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_card_defaults_to_debit(self):
        res = self.client.post(
            "/api/cards/",
            {
                "card_number": "5234567890123456",
                "expiry_month": 12,
                "expiry_year": 2030,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["card_type"], "debit")
        self.assertEqual(res.data["card_network"], "mastercard")

    def test_create_card_invalid_expiry_month_zero(self):
        res = self.client.post(
            "/api/cards/",
            {
                "card_number": "4242424242424242",
                "card_type": "debit",
                "expiry_month": 0,
                "expiry_year": 2030,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_card_invalid_expiry_month_thirteen(self):
        res = self.client.post(
            "/api/cards/",
            {
                "card_number": "4242424242424242",
                "card_type": "debit",
                "expiry_month": 13,
                "expiry_year": 2030,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_card_expired_same_year_earlier_month(self):
        from datetime import date

        today = date.today()
        if today.month > 1:
            res = self.client.post(
                "/api/cards/",
                {
                    "card_number": "4242424242424242",
                    "card_type": "debit",
                    "expiry_month": 1,
                    "expiry_year": today.year,
                },
            )
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_card_expiry_month_not_provided_defaults_debit(self):
        res = self.client.post(
            "/api/cards/",
            {
                "card_number": "4242424242424242",
                "expiry_month": 6,
                "expiry_year": 2030,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["card_type"], "debit")


class CardBlockViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.card = Card.objects.create(
            user=self.user,
            last_four="1234",
            card_type="debit",
            expiry_month=12,
            expiry_year=2030,
        )
        self.client.force_authenticate(user=self.user)

    def test_block_card(self):
        res = self.client.patch(f"/api/cards/{self.card.pk}/block/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.card.refresh_from_db()
        self.assertEqual(self.card.status, "blocked")

    def test_block_already_blocked(self):
        self.card.status = "blocked"
        self.card.save()
        res = self.client.patch(f"/api/cards/{self.card.pk}/block/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_block_other_users_card(self):
        other = make_user("01700000002", "2222222222")
        other_card = Card.objects.create(
            user=other,
            last_four="5678",
            card_type="prepaid",
            expiry_month=6,
            expiry_year=2029,
        )
        res = self.client.patch(f"/api/cards/{other_card.pk}/block/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_block_nonexistent(self):
        res = self.client.patch("/api/cards/9999/block/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class CardUnblockViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.card = Card.objects.create(
            user=self.user,
            last_four="1234",
            card_type="debit",
            expiry_month=12,
            expiry_year=2030,
            status="blocked",
        )
        self.client.force_authenticate(user=self.user)

    def test_unblock_card(self):
        res = self.client.patch(f"/api/cards/{self.card.pk}/unblock/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.card.refresh_from_db()
        self.assertEqual(self.card.status, "active")

    def test_unblock_not_blocked(self):
        self.card.status = "active"
        self.card.save()
        res = self.client.patch(f"/api/cards/{self.card.pk}/unblock/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unblock_other_users_card(self):
        other = make_user("01700000002", "2222222222")
        other_card = Card.objects.create(
            user=other,
            last_four="5678",
            card_type="prepaid",
            expiry_month=6,
            expiry_year=2029,
            status="blocked",
        )
        res = self.client.patch(f"/api/cards/{other_card.pk}/unblock/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
