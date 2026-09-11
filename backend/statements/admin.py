from django.contrib import admin

from .models import AccountStatement


@admin.register(AccountStatement)
class AccountStatementAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "year",
        "month",
        "opening_balance",
        "closing_balance",
        "transaction_count",
        "generated_at",
    ]
    search_fields = ["user__phone"]
    ordering = ["-year", "-month"]
