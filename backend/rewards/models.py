from django.conf import settings
from django.db import models


class Reward(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reward_account",
    )
    points = models.PositiveIntegerField(default=0)
    lifetime_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reward"
        verbose_name_plural = "Rewards"

    def __str__(self):
        return f"{self.user.phone} - {self.points} points"


class PointsTransaction(models.Model):
    TYPE_CHOICES = [
        ("earn", "Earned"),
        ("redeem", "Redeemed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="points_transactions",
    )
    points = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Points Transaction"
        verbose_name_plural = "Points Transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.phone} {'+' if self.transaction_type == 'earn' else '-'}{self.points}pts"


class Offer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    points_required = models.PositiveIntegerField(default=0)
    cashback_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    cashback_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    category = models.CharField(max_length=50, default="general")
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ["-valid_from"]

    def __str__(self):
        return self.title


class UserOffer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_offers",
    )
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="users")
    is_claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Offer"
        verbose_name_plural = "User Offers"
        unique_together = [["user", "offer"]]

    def __str__(self):
        return f"{self.user.phone} - {self.offer.title}"
