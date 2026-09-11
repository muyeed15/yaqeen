from django.contrib import admin

from .models import Biller, BillerCategory, BillPayment


@admin.register(BillerCategory)
class BillerCategoryAdmin(admin.ModelAdmin):
    list_display = ["key", "label", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["key", "label"]


@admin.register(Biller)
class BillerAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "biller_code", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "biller_code"]


@admin.register(BillPayment)
class BillPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "user",
        "biller",
        "account_number",
        "amount",
        "status",
        "created_at",
    ]
    list_filter = ["status", "biller"]
    search_fields = ["reference", "user__phone", "account_number"]
    ordering = ["-created_at"]
