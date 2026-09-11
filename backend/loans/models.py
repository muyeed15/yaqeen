import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class QardHasanProduct(models.Model):
    name = models.CharField(max_length=100)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure_days = models.PositiveIntegerField(help_text="Repayment period in days")
    service_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Flat service fee (not percentage-based riba)",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Qard Hasan Product"
        verbose_name_plural = "Qard Hasan Products"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - up to ৳{self.max_amount}"


class QardHasanApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("disbursed", "Disbursed"),
        ("repaid", "Repaid"),
        ("rejected", "Rejected"),
        ("overdue", "Overdue"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="qard_hasan_applications",
    )
    product = models.ForeignKey(
        QardHasanProduct, on_delete=models.PROTECT, related_name="applications"
    )
    loan_reference = models.CharField(max_length=20, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    hibah_given = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Voluntary gift from borrower on top of principal",
    )
    tenure_days = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    due_date = models.DateField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Qard Hasan Application"
        verbose_name_plural = "Qard Hasan Applications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.loan_reference:
            self.loan_reference = "QH" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.loan_reference} - {self.user.phone}"


class QardHasanRepayment(models.Model):
    application = models.ForeignKey(
        QardHasanApplication, on_delete=models.CASCADE, related_name="repayments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    hibah = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Voluntary extra payment as gift",
    )
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Qard Hasan Repayment"
        verbose_name_plural = "Qard Hasan Repayments"
        ordering = ["-paid_at"]

    def __str__(self):
        return f"Repay {self.application.loan_reference} - ৳{self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        app = self.application
        app.amount_paid += self.amount
        app.hibah_given += self.hibah
        if app.amount_paid >= app.amount_due:
            app.status = "repaid"
        app.save(update_fields=["amount_paid", "hibah_given", "status"])
