from django.contrib import admin

from .models import DataPack, Operator, OperatorType, RechargeTransaction


@admin.register(OperatorType)
class OperatorTypeAdmin(admin.ModelAdmin):
    list_display = ["key", "label", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["key", "label"]


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ["name", "operator_code", "type", "is_active"]
    list_filter = ["type", "is_active"]
    search_fields = ["name", "operator_code"]


@admin.register(DataPack)
class DataPackAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "operator",
        "volume",
        "validity_days",
        "amount",
        "is_active",
    ]
    list_filter = ["operator", "is_active"]


@admin.register(RechargeTransaction)
class RechargeTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "user",
        "operator",
        "phone_number",
        "amount",
        "recharge_type",
        "status",
        "created_at",
    ]
    list_filter = ["recharge_type", "status", "operator"]
    search_fields = ["reference", "phone_number", "user__phone"]
    ordering = ["-created_at"]
