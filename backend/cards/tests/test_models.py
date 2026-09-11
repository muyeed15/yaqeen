from django.test import TestCase

from cards.models import Card
from common.tests.helpers import make_user


class CardModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.card = Card.objects.create(
            user=self.user,
            last_four="1234",
            card_type="debit",
            expiry_month=12,
            expiry_year=2030,
        )

    def test_str(self):
        expected = "01700000001 - visa ***1234"
        self.assertEqual(str(self.card), expected)

    def test_default_status_is_active(self):
        self.assertEqual(self.card.status, "active")

    def test_default_card_type_is_debit(self):
        card = Card.objects.create(
            user=self.user,
            last_four="5678",
            expiry_month=6,
            expiry_year=2029,
        )
        self.assertEqual(card.card_type, "debit")

    def test_user_relation(self):
        self.assertEqual(self.card.user, self.user)

    def test_ordering(self):
        card2 = Card.objects.create(
            user=self.user,
            last_four="5678",
            expiry_month=6,
            expiry_year=2029,
        )
        qs = Card.objects.all()
        self.assertEqual(qs.first(), card2)

    def test_invalid_expiry_month_boundary(self):
        with self.assertRaises(Exception):
            Card.objects.create(
                user=self.user,
                last_four="0000",
                expiry_month=0,
                expiry_year=2030,
            )

    def test_max_expiry_month_boundary(self):
        card = Card.objects.create(
            user=self.user,
            last_four="0000",
            expiry_month=12,
            expiry_year=2030,
        )
        self.assertEqual(card.expiry_month, 12)

    def test_prepaid_card_type(self):
        card = Card.objects.create(
            user=self.user,
            last_four="9999",
            card_type="prepaid",
            expiry_month=6,
            expiry_year=2030,
        )
        self.assertEqual(card.card_type, "prepaid")
