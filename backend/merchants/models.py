from django.conf import settings
from django.db import models


class MerchantCategory(models.Model):
    key = models.CharField(max_length=15, unique=True)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Merchant Category"
        verbose_name_plural = "Merchant Categories"
        ordering = ["label"]

    def __str__(self):
        return self.label


class VerifiedMerchantManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_verified=True)


class Merchant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="merchant_profile",
    )
    business_name = models.CharField(max_length=150)
    category = models.ForeignKey(
        MerchantCategory,
        on_delete=models.PROTECT,
        related_name="merchants",
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    verified = VerifiedMerchantManager()

    class Meta:
        verbose_name = "Merchant"
        verbose_name_plural = "Merchants"
        ordering = ["business_name"]
        indexes = [
            models.Index(fields=["is_verified"]),
        ]

    def __str__(self):
        return (
            f"{self.business_name} ({self.category.label if self.category_id else ''})"
        )
