from decimal import Decimal

from django.test import TestCase

from common.tests.helpers import make_user
from savings.models import MudarabahAccount, MudarabahContribution, MudarabahPlan


class MudarabahPlanModelTest(TestCase):
    def setUp(self):
        self.plan = MudarabahPlan.objects.create(
            name="Basic Plan",
            duration_months=6,
            monthly_amount=Decimal("500.00"),
            profit_ratio=Decimal("50.00"),
        )

    def test_str(self):
        expected = "Basic Plan - ৳500.00/mo x 6m"
        self.assertEqual(str(self.plan), expected)

    def test_default_is_active(self):
        self.assertTrue(self.plan.is_active)

    def test_zero_duration_plan(self):
        plan = MudarabahPlan.objects.create(
            name="Zero Month",
            duration_months=0,
            monthly_amount=Decimal("0.00"),
            profit_ratio=Decimal("0.00"),
        )
        self.assertEqual(plan.duration_months, 0)

    def test_plan_with_zero_monthly_amount(self):
        plan = MudarabahPlan.objects.create(
            name="Free Plan",
            duration_months=12,
            monthly_amount=Decimal("0.00"),
            profit_ratio=Decimal("10.00"),
        )
        self.assertEqual(plan.monthly_amount, Decimal("0.00"))

    def test_all_fields_in_str(self):
        self.assertIn("500.00", str(self.plan))
        self.assertIn("6m", str(self.plan))


class MudarabahAccountModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.plan = MudarabahPlan.objects.create(
            name="Basic Plan",
            duration_months=6,
            monthly_amount=Decimal("500.00"),
            profit_ratio=Decimal("50.00"),
        )
        self.account = MudarabahAccount.objects.create(
            user=self.user,
            plan=self.plan,
        )

    def test_str(self):
        self.assertIn(self.user.phone, str(self.account))

    def test_account_number_generated(self):
        self.assertTrue(self.account.account_number.startswith("MUD"))

    def test_maturity_date_set(self):
        self.assertIsNotNone(self.account.maturity_date)

    def test_default_status_active(self):
        self.assertEqual(self.account.status, "active")

    def test_update_expected_payout(self):
        self.account.total_deposited = Decimal("3000.00")
        self.account.update_expected_payout()
        projected = self.plan.monthly_amount * self.plan.duration_months
        profit = projected * (self.plan.profit_ratio / Decimal("100"))
        expected = Decimal("3000.00") + profit
        self.assertEqual(self.account.expected_payout, expected)


class MudarabahContributionModelTest(TestCase):
    def setUp(self):
        self.user = make_user("01700000001", "1111111111")
        self.plan = MudarabahPlan.objects.create(
            name="Basic Plan",
            duration_months=6,
            monthly_amount=Decimal("500.00"),
            profit_ratio=Decimal("50.00"),
        )
        self.account = MudarabahAccount.objects.create(
            user=self.user,
            plan=self.plan,
        )
        self.contribution = MudarabahContribution.objects.create(
            mudarabah_account=self.account,
            installment_number=1,
            amount=Decimal("500.00"),
        )

    def test_str(self):
        self.assertIn(f"#{self.contribution.installment_number}", str(self.contribution))

    def test_default_status_paid(self):
        self.assertEqual(self.contribution.status, "paid")

    def test_unique_together(self):
        with self.assertRaises(Exception):
            MudarabahContribution.objects.create(
                mudarabah_account=self.account,
                installment_number=1,
                amount=Decimal("500.00"),
            )

    def test_missed_contribution_status(self):
        c = MudarabahContribution.objects.create(
            mudarabah_account=self.account,
            installment_number=2,
            amount=Decimal("500.00"),
            status="missed",
        )
        self.assertEqual(c.status, "missed")
