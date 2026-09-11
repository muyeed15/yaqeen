import uuid

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    TYPE_CHOICES = [
        ("send", "Send Money"),
        ("cash_in", "Cash In"),
        ("cash_out", "Cash Out"),
        ("payment", "QR Payment"),
        ("bill", "Bill Payment"),
        ("recharge", "Mobile Recharge"),
        ("bank", "Bank Transfer"),
        ("savings", "Savings"),
        ("charity", "Charity"),
        ("loan", "Qard Hasan"),
        ("ticket", "Ticket Booking"),
        ("remittance", "Remittance"),
        ("gateway", "Gateway Payment"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("reversed", "Reversed"),
    ]

    reference_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_transactions",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_transactions",
    )
    merchant = models.ForeignKey(
        "merchants.Merchant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_payments",
    )
    counterparty = models.CharField(max_length=150, blank=True, default="")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sender", "-created_at"]),
            models.Index(fields=["receiver", "-created_at"]),
            models.Index(fields=["merchant", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.reference_id} - {self.transaction_type} - {self.status}"


class MoneyRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("expired", "Expired"),
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_money_requests",
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_money_requests",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Money Request"
        verbose_name_plural = "Money Requests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["requester", "-created_at"]),
            models.Index(fields=["target", "-created_at"]),
        ]

    def __str__(self):
        return f"Req #{self.id} - {self.requester.phone} -> {self.target.phone} ৳{self.amount}"
