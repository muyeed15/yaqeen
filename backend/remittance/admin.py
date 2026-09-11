from django.contrib import admin

from .models import RemittancePartner, RemittanceTransaction


@admin.register(RemittancePartner)
class RemittancePartnerAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "currency", "exchange_rate", "is_active"]
    list_filter = ["country", "is_active"]


@admin.register(RemittanceTransaction)
class RemittanceTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "reference_number",
        "user",
        "partner",
        "amount_foreign",
        "amount_bdt",
        "status",
        "created_at",
    ]
    list_filter = ["status", "partner"]
    search_fields = ["reference_number", "user__phone"]
    ordering = ["-created_at"]
