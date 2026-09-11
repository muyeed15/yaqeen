import base64

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def _mask(value):
    if not value or len(value) < 6:
        return "****"
    return value[:6] + "*" * (len(value) - 10) + value[-4:]


class Card(models.Model):
    CARD_TYPE_CHOICES = [
        ("debit", "Debit Card"),
        ("prepaid", "Prepaid Card"),
    ]

    CARD_NETWORK_CHOICES = [
        ("visa", "Visa"),
        ("mastercard", "Mastercard"),
        ("amex", "American Express"),
        ("nexus", "Nexus"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("blocked", "Blocked"),
        ("expired", "Expired"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    card_network = models.CharField(
        max_length=12, choices=CARD_NETWORK_CHOICES, default="visa"
    )
    last_four = models.CharField(max_length=4, editable=False, default="****")
    masked_number = models.CharField(max_length=19, editable=False, default="****")
    _number = models.TextField(db_column="card_number", default="")
    cardholder_name = models.CharField(max_length=100, default="")
    card_type = models.CharField(
        max_length=10, choices=CARD_TYPE_CHOICES, default="debit"
    )
    expiry_month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    expiry_year = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Card"
        verbose_name_plural = "Cards"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(expiry_month__gte=1, expiry_month__lte=12),
                name="card_valid_expiry_month",
            ),
        ]

    def set_number(self, raw_number):
        self._number = base64.b64encode(raw_number.encode()).decode()
        self.last_four = raw_number[-4:]
        self.masked_number = _mask(raw_number)

    def __str__(self):
        return f"{self.user.phone} - {self.card_network} ***{self.last_four}"
