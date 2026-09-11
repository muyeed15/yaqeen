from django.contrib import admin

from .models import MudarabahAccount, MudarabahContribution, MudarabahPlan


@admin.register(MudarabahPlan)
class MudarabahPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "monthly_amount", "duration_months", "profit_ratio", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


class MudarabahContributionInline(admin.TabularInline):
    model = MudarabahContribution
    extra = 0
    readonly_fields = ["installment_number", "amount", "status", "paid_at"]


@admin.register(MudarabahAccount)
class MudarabahAccountAdmin(admin.ModelAdmin):
    list_display = [
        "account_number",
        "user",
        "plan",
        "status",
        "start_date",
        "maturity_date",
        "total_deposited",
    ]
    list_filter = ["status"]
    search_fields = ["account_number", "user__phone"]
    inlines = [MudarabahContributionInline]
