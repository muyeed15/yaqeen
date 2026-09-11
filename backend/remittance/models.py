import uuid

from django.conf import settings
from django.db import models


class RemittancePartner(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, help_text="ISO 4217 currency code")
    exchange_rate = models.DecimalField(max_digits=8, decimal_places=2)
    logo = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Remittance Partner"
        verbose_name_plural = "Remittance Partners"
        ordering = ["country", "name"]

    def __str__(self):
        return f"{self.name} ({self.country})"


class RemittanceTransaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="remittance_transactions",
    )
    partner = models.ForeignKey(
        RemittancePartner, on_delete=models.PROTECT, related_name="remittances"
    )
    sender_name = models.CharField(max_length=100)
    sender_country = models.CharField(max_length=50)
    amount_foreign = models.DecimalField(max_digits=10, decimal_places=2)
    amount_bdt = models.DecimalField(max_digits=12, decimal_places=2)
    exchange_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Spot exchange rate per Sarraf/Hawala principles",
    )
    reference_number = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Remittance Transaction"
        verbose_name_plural = "Remittance Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = "RMT" + uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.phone} - {self.partner.currency} {self.amount_foreign}"
