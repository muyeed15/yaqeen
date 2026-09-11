from django.contrib import admin

from .models import Bank, BankAccount, BankTransaction


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ["name", "bank_code", "is_islamic", "is_active"]
    list_filter = ["is_islamic", "is_active"]
    search_fields = ["name", "bank_code"]


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "bank", "account_holder", "account_number", "is_verified"]
    list_filter = ["bank", "is_verified"]
    search_fields = ["user__phone", "account_number"]


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "user",
        "bank_account",
        "amount",
        "transaction_type",
        "status",
        "created_at",
    ]
    list_filter = ["transaction_type", "status"]
    search_fields = ["reference", "user__phone"]
    ordering = ["-created_at"]
