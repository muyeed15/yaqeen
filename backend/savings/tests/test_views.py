from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from common.tests.helpers import make_user, make_wallet
from savings.models import MudarabahAccount, MudarabahContribution, MudarabahPlan


class MudarabahPlanListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)
        self.plan = MudarabahPlan.objects.create(
            name="Active Plan",
            duration_months=6,
            monthly_amount=Decimal("500.00"),
            profit_ratio=Decimal("50.00"),
        )
        MudarabahPlan.objects.create(
            name="Inactive Plan",
            duration_months=3,
            monthly_amount=Decimal("300.00"),
            profit_ratio=Decimal("40.00"),
            is_active=False,
        )

    def test_list_only_active_plans(self):
        res = self.client.get("/api/mudarabah/plans/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], "Active Plan")

    def test_no_active_plans(self):
        MudarabahPlan.objects.all().update(is_active=False)
        res = self.client.get("/api/mudarabah/plans/")
        self.assertEqual(len(res.data), 0)


class MudarabahAccountListCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        make_wallet(self.user, "5000.00")
        self.plan = MudarabahPlan.objects.create(
            name="Basic Plan",
            duration_months=6,
            monthly_amount=Decimal("500.00"),
            profit_ratio=Decimal("50.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_list_accounts_empty(self):
        res = self.client.get("/api/mudarabah/accounts/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_create_account_success(self):
        res = self.client.post(
            "/api/mudarabah/accounts/",
            {
                "plan_id": self.plan.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("account_number", res.data)
        self.assertEqual(MudarabahAccount.objects.count(), 1)
        self.assertEqual(MudarabahContribution.objects.count(), 1)

    def test_create_account_insufficient_balance(self):
        wallet = self.user.wallet
        wallet.balance = Decimal("10.00")
        wallet.save()
        res = self.client.post(
            "/api/mudarabah/accounts/",
            {
                "plan_id": self.plan.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_account_inactive_plan(self):
        inactive = MudarabahPlan.objects.create(
            name="Inactive",
            duration_months=3,
            monthly_amount=Decimal("100.00"),
            profit_ratio=Decimal("30.00"),
            is_active=False,
        )
        res = self.client.post(
            "/api/mudarabah/accounts/",
            {
                "plan_id": inactive.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_account_deducts_first_contribution(self):
        self.client.post(
            "/api/mudarabah/accounts/",
            {
                "plan_id": self.plan.pk,
            },
        )
        wallet = self.user.wallet
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("4500.00"))

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/mudarabah/accounts/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_account_exact_balance(self):
        wallet = self.user.wallet
        wallet.balance = Decimal("500.00")
        wallet.save()
        res = self.client.post(
            "/api/mudarabah/accounts/",
            {
                "plan_id": self.plan.pk,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("0.00"))


class MudarabahAccountDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.plan = MudarabahPlan.objects.create(
            name="Basic Plan",
            duration_months=6,
            monthly_amount=Decimal("500.00"),
            profit_ratio=Decimal("50.00"),
        )
        self.account = MudarabahAccount.objects.create(user=self.user, plan=self.plan)
        self.client.force_authenticate(user=self.user)

    def test_get_detail(self):
        res = self.client.get(f"/api/mudarabah/accounts/{self.account.account_number}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["account_number"], self.account.account_number)

    def test_get_other_users_account(self):
        other = make_user("01700000002", "2222222222")
        other_account = MudarabahAccount.objects.create(user=other, plan=self.plan)
        res = self.client.get(f"/api/mudarabah/accounts/{other_account.account_number}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class MudarabahContributionHistoryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.plan = MudarabahPlan.objects.create(
            name="Basic Plan",
            duration_months=6,
            monthly_amount=Decimal("500.00"),
            profit_ratio=Decimal("50.00"),
        )
        self.account = MudarabahAccount.objects.create(user=self.user, plan=self.plan)
        MudarabahContribution.objects.create(
            mudarabah_account=self.account,
            installment_number=1,
            amount=Decimal("500.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_list_contributions(self):
        res = self.client.get(
            f"/api/mudarabah/accounts/{self.account.account_number}/contributions/"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_other_users_account_returns_404(self):
        other = make_user("01700000002", "2222222222")
        other_account = MudarabahAccount.objects.create(user=other, plan=self.plan)
        res = self.client.get(
            f"/api/mudarabah/accounts/{other_account.account_number}/contributions/"
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class PayMudarabahContributionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        make_wallet(self.user, "5000.00")
        self.plan = MudarabahPlan.objects.create(
            name="Basic Plan",
            duration_months=3,
            monthly_amount=Decimal("500.00"),
            profit_ratio=Decimal("50.00"),
        )
        self.account = MudarabahAccount.objects.create(user=self.user, plan=self.plan)
        MudarabahContribution.objects.create(
            mudarabah_account=self.account,
            installment_number=1,
            amount=Decimal("500.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_pay_contribution_success(self):
        res = self.client.post(
            "/api/mudarabah/pay/",
            {
                "account_number": self.account.account_number,
                "amount": "500.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(MudarabahContribution.objects.count(), 2)

    def test_pay_contribution_updates_account(self):
        self.account.total_deposited = Decimal("500.00")
        self.account.save()
        self.client.post(
            "/api/mudarabah/pay/",
            {
                "account_number": self.account.account_number,
                "amount": "500.00",
            },
        )
        self.account.refresh_from_db()
        self.assertEqual(self.account.total_deposited, Decimal("1000.00"))

    def test_insufficient_balance(self):
        wallet = self.user.wallet
        wallet.balance = Decimal("10.00")
        wallet.save()
        res = self.client.post(
            "/api/mudarabah/pay/",
            {
                "account_number": self.account.account_number,
                "amount": "500.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pay_last_contribution_matures_account(self):
        MudarabahContribution.objects.create(
            mudarabah_account=self.account,
            installment_number=2,
            amount=Decimal("500.00"),
        )
        res = self.client.post(
            "/api/mudarabah/pay/",
            {
                "account_number": self.account.account_number,
                "amount": "500.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(self.account.status, "matured")

    def test_pay_exceeding_plan_duration(self):
        MudarabahContribution.objects.create(
            mudarabah_account=self.account,
            installment_number=2,
            amount=Decimal("500.00"),
        )
        MudarabahContribution.objects.create(
            mudarabah_account=self.account,
            installment_number=3,
            amount=Decimal("500.00"),
        )
        res = self.client.post(
            "/api/mudarabah/pay/",
            {
                "account_number": self.account.account_number,
                "amount": "500.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_users_account(self):
        other = make_user("01700000002", "2222222222")
        other_account = MudarabahAccount.objects.create(user=other, plan=self.plan)
        res = self.client.post(
            "/api/mudarabah/pay/",
            {
                "account_number": other_account.account_number,
                "amount": "500.00",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
