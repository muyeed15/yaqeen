from django.conf import settings
from django.db import models


class BillerCategory(models.Model):
    key = models.CharField(max_length=15, unique=True)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Biller Category"
        verbose_name_plural = "Biller Categories"
        ordering = ["label"]

    def __str__(self):
        return self.label


class Biller(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        BillerCategory,
        on_delete=models.PROTECT,
        related_name="billers",
    )
    biller_code = models.CharField(max_length=20, unique=True)
    logo = models.FileField(upload_to="billers/", blank=True)
    account_no_label = models.CharField(max_length=50, default="Account Number")
    amount_no_label = models.CharField(max_length=50, default="Bill Number")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Biller"
        verbose_name_plural = "Billers"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.category.label if self.category_id else ''})"


class BillPayment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bill_payments",
    )
    biller = models.ForeignKey(
        Biller, on_delete=models.PROTECT, related_name="payments"
    )
    account_number = models.CharField(max_length=50)
    bill_number = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    bill_month = models.CharField(max_length=10, blank=True)
    reference = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bill Payment"
        verbose_name_plural = "Bill Payments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["biller", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.phone} - {self.biller.name} - ৳{self.amount}"
