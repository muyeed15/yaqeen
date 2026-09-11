import uuid

from django.conf import settings
from django.db import models


class PaymentGateway(models.Model):
    merchant = models.OneToOneField(
        "merchants.Merchant", on_delete=models.CASCADE, related_name="gateway"
    )
    api_key = models.CharField(max_length=64, unique=True, editable=False)
    webhook_url = models.URLField(blank=True)
    callback_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Gateway"
        verbose_name_plural = "Payment Gateways"

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = uuid.uuid4().hex + uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Gateway - {self.merchant.business_name}"


class GatewayTransaction(models.Model):
    STATUS_CHOICES = [
        ("initiated", "Initiated"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    gateway = models.ForeignKey(
        PaymentGateway, on_delete=models.PROTECT, related_name="transactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gateway_transactions",
    )
    txn_id = models.CharField(max_length=50, unique=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    order_id = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="initiated"
    )
    callback_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gateway Transaction"
        verbose_name_plural = "Gateway Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["gateway", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.txn_id:
            self.txn_id = "GTW" + uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.txn_id} - ৳{self.amount}"
