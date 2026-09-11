from django.contrib import admin

from .models import Agent, AgentTransaction


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["shop_name", "full_name", "phone", "district", "thana", "is_verified", "status"]
    list_filter = ["district", "status", "is_verified"]
    search_fields = ["shop_name", "full_name", "phone"]


@admin.register(AgentTransaction)
class AgentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "user",
        "agent",
        "amount",
        "transaction_type",
        "status",
        "created_at",
    ]
    list_filter = ["transaction_type", "status"]
    search_fields = ["reference", "user__phone"]
    ordering = ["-created_at"]
