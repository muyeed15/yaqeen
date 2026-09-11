from django.conf import settings
from django.db import models


class AccountStatement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_statements",
    )
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2)
    total_credits = models.DecimalField(max_digits=12, decimal_places=2)
    total_debits = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = models.PositiveIntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Account Statement"
        verbose_name_plural = "Account Statements"
        ordering = ["-year", "-month"]
        unique_together = [["user", "year", "month"]]

    def __str__(self):
        return f"Statement {self.year}-{self.month:02d} - {self.user.phone}"
