from decimal import Decimal

from django.test import TestCase

from common.tests.helpers import make_user
from transactions.models import Transaction


class TransactionModelTest(TestCase):
    def setUp(self):
        self.sender = make_user("01700000001", "1111111111")
        self.receiver = make_user("01700000002", "2222222222")
        self.tx = Transaction.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal("100.00"),
            fee=Decimal("1.50"),
            transaction_type="send",
            status="completed",
        )

    def test_str(self):
        expected = f"{self.tx.reference_id} - send - completed"
        self.assertEqual(str(self.tx), expected)

    def test_default_status_is_pending(self):
        tx = Transaction.objects.create(
            sender=self.sender,
            amount=Decimal("50.00"),
            transaction_type="cash_in",
        )
        self.assertEqual(tx.status, "pending")

    def test_reference_id_is_uuid(self):
        self.assertIsNotNone(self.tx.reference_id)

    def test_sender_relation(self):
        self.assertEqual(self.tx.sender, self.sender)

    def test_receiver_relation(self):
        self.assertEqual(self.tx.receiver, self.receiver)

    def test_transaction_with_note(self):
        tx = Transaction.objects.create(
            sender=self.sender,
            amount=Decimal("25.00"),
            transaction_type="send",
            note="Test note here",
        )
        self.assertEqual(tx.note, "Test note here")

    def test_transaction_null_sender(self):
        tx = Transaction.objects.create(
            receiver=self.receiver,
            amount=Decimal("50.00"),
            transaction_type="cash_in",
        )
        self.assertIsNone(tx.sender)

    def test_transaction_all_types(self):
        for ttype, _ in Transaction.TYPE_CHOICES:
            tx = Transaction.objects.create(
                sender=self.sender,
                amount=Decimal("10.00"),
                transaction_type=ttype,
            )
            self.assertEqual(tx.transaction_type, ttype)

    def test_transaction_all_statuses(self):
        for status_val, _ in Transaction.STATUS_CHOICES:
            tx = Transaction.objects.create(
                sender=self.sender,
                amount=Decimal("10.00"),
                transaction_type="send",
                status=status_val,
            )
            self.assertEqual(tx.status, status_val)

    def test_default_fee_is_zero(self):
        tx = Transaction.objects.create(
            sender=self.sender,
            amount=Decimal("100.00"),
            transaction_type="send",
        )
        self.assertEqual(tx.fee, Decimal("0.00"))
