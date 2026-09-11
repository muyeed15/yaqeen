import uuid
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


class MudarabahPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_months = models.PositiveIntegerField()
    monthly_amount = models.DecimalField(max_digits=12, decimal_places=2)
    profit_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Mudarabah profit-sharing ratio (e.g., 50.00 = 50%)",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mudarabah Plan"
        verbose_name_plural = "Mudarabah Plans"
        ordering = ["duration_months", "monthly_amount"]

    def __str__(self):
        return f"{self.name} - ৳{self.monthly_amount}/mo x {self.duration_months}m"


class MudarabahAccount(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("matured", "Matured"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mudarabah_accounts",
    )
    plan = models.ForeignKey(
        MudarabahPlan, on_delete=models.PROTECT, related_name="accounts"
    )
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    start_date = models.DateField(default=timezone.localdate)
    maturity_date = models.DateField()
    total_deposited = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    expected_payout = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mudarabah Account"
        verbose_name_plural = "Mudarabah Accounts"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = "MUD" + uuid.uuid4().hex[:9].upper()
        if not self.maturity_date:
            self.maturity_date = self.start_date + relativedelta(
                months=self.plan.duration_months
            )
        super().save(*args, **kwargs)

    def update_expected_payout(self):
        projected = self.plan.monthly_amount * self.plan.duration_months
        profit = projected * (self.plan.profit_ratio / Decimal("100"))
        self.expected_payout = self.total_deposited + profit

    def __str__(self):
        return f"{self.account_number} - {self.user.phone}"


class MudarabahContribution(models.Model):
    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("missed", "Missed"),
    ]

    mudarabah_account = models.ForeignKey(
        MudarabahAccount, on_delete=models.CASCADE, related_name="contributions"
    )
    installment_number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="paid")
    paid_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mudarabah Contribution"
        verbose_name_plural = "Mudarabah Contributions"
        ordering = ["installment_number"]
        unique_together = [["mudarabah_account", "installment_number"]]

    def __str__(self):
        return f"{self.mudarabah_account.account_number} - #{self.installment_number}"
