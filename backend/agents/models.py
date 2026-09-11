from django.conf import settings
from django.db import models


class Agent(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("suspended", "Suspended"),
    ]

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    nid = models.CharField(max_length=20, unique=True)
    shop_name = models.CharField(max_length=150)
    district = models.CharField(max_length=50)
    thana = models.CharField(max_length=50)
    address = models.TextField()
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    is_verified = models.BooleanField(default=False)
    commission_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text="Wakalah fee percentage for agent services",
    )
    daily_limit = models.DecimalField(max_digits=12, decimal_places=2, default=50000.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
        ordering = ["shop_name"]
        indexes = [
            models.Index(fields=["district", "status"]),
        ]

    def __str__(self):
        return f"{self.shop_name} ({self.phone})"


class AgentTransaction(models.Model):
    TYPE_CHOICES = [
        ("cash_in", "Cash In"),
        ("cash_out", "Cash Out"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agent_transactions",
    )
    agent = models.ForeignKey(
        Agent, on_delete=models.PROTECT, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    commission = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    reference = models.CharField(max_length=50, unique=True)
    otp = models.CharField(max_length=6, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Agent Transaction"
        verbose_name_plural = "Agent Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["agent", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.user.phone} - ৳{self.amount}"
