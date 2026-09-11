from django.contrib import admin

from .models import GatewayTransaction, PaymentGateway


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ["merchant", "api_key", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["merchant__business_name"]


@admin.register(GatewayTransaction)
class GatewayTransactionAdmin(admin.ModelAdmin):
    list_display = ["txn_id", "gateway", "user", "amount", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["txn_id", "user__phone"]
    ordering = ["-created_at"]
