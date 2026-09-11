from django.contrib import admin

from .models import QardHasanApplication, QardHasanProduct, QardHasanRepayment


@admin.register(QardHasanProduct)
class QardHasanProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "min_amount",
        "max_amount",
        "tenure_days",
        "service_fee",
        "is_active",
    ]
    list_filter = ["is_active"]


@admin.register(QardHasanApplication)
class QardHasanApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "loan_reference",
        "user",
        "product",
        "amount",
        "amount_due",
        "amount_paid",
        "status",
        "due_date",
    ]
    list_filter = ["status", "product"]
    search_fields = ["loan_reference", "user__phone"]
    ordering = ["-created_at"]


@admin.register(QardHasanRepayment)
class QardHasanRepaymentAdmin(admin.ModelAdmin):
    list_display = ["application", "amount", "hibah", "paid_at"]
    ordering = ["-paid_at"]
