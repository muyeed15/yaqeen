from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


class ZakatPayment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="zakat_payments"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_zakat",
        help_text="Foundation receiving this zakat",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    asset_type = models.CharField(
        max_length=50, blank=True, null=True, help_text="e.g., cash, gold, silver, business"
    )
    hawl_year = models.PositiveIntegerField(
        blank=True, null=True, help_text="The lunar year this zakat covers"
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Zakat Payment"
        verbose_name_plural = "Zakat Payments"
        ordering = ["-paid_at"]

    def __str__(self):
        return f"Zakat({self.id}) - {self.user.phone} - ৳{self.amount}"


class Sadaqah(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sadaqah_donations"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_sadaqah",
        help_text="Foundation receiving this sadaqah",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    cause = models.ForeignKey(
        "accounts.CharityCause",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sadaqah_donations",
        help_text="Optional cause this sadaqah supports",
    )
    is_anonymous = models.BooleanField(default=False)
    given_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sadaqah"
        verbose_name_plural = "Sadaqah"
        ordering = ["-given_at"]

    def __str__(self):
        return f"Sadaqah({self.id}) - {self.user.phone} - ৳{self.amount}"


class HawlTracking(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hawl_tracking"
    )
    nisab_crossed_at = models.DateTimeField(
        blank=True, null=True, help_text="When the user's wealth first crossed the nisab threshold"
    )
    next_hawl_date = models.DateField(
        blank=True, null=True, help_text="One lunar year after nisab_crossed_at; zakat becomes due"
    )
    is_eligible = models.BooleanField(
        default=False, help_text="Whether the user currently has wealth above nisab"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hawl Tracking"
        verbose_name_plural = "Hawl Tracking"

    def __str__(self):
        return f"HawL({self.user.phone}) - next: {self.next_hawl_date}"


class SadaqahJariyah(models.Model):
    FREQUENCY_CHOICES = [
        ("monthly", "Monthly"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sadaqah_jariyah_donations"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_sadaqah_jariyah",
        help_text="Foundation receiving this sadaqah jariyah",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    cause = models.ForeignKey(
        "accounts.CharityCause",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sadaqah_jariyah_donations",
        help_text="Recurring cause (e.g., water well, education fund)",
    )
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="monthly")
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(default=timezone.localdate)
    next_due_date = models.DateField(blank=True, null=True)
    total_donated = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sadaqah Jariyah"
        verbose_name_plural = "Sadaqah Jariyah"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.next_due_date:
            self.next_due_date = self.start_date + relativedelta(months=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SJ({self.id}) - {self.user.phone} - ৳{self.amount}/{self.frequency}"
