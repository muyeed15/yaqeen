from django.contrib import admin

from accounts.models import CharityCause

from .models import HawlTracking, Sadaqah, SadaqahJariyah, ZakatPayment


@admin.register(CharityCause)
class CharityCauseAdmin(admin.ModelAdmin):
    list_display = ["key", "label", "icon", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["key", "label"]


@admin.register(ZakatPayment)
class ZakatPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "recipient",
        "amount",
        "asset_type",
        "hawl_year",
        "paid_at",
    ]
    list_filter = ["hawl_year"]
    search_fields = ["user__phone", "recipient__phone"]


@admin.register(Sadaqah)
class SadaqahAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "recipient",
        "amount",
        "cause",
        "is_anonymous",
        "given_at",
    ]
    list_filter = ["is_anonymous"]
    search_fields = ["user__phone", "cause", "recipient__phone"]


@admin.register(HawlTracking)
class HawlTrackingAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "nisab_crossed_at",
        "next_hawl_date",
        "is_eligible",
        "updated_at",
    ]
    list_filter = ["is_eligible"]
    search_fields = ["user__phone"]


@admin.register(SadaqahJariyah)
class SadaqahJariyahAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "recipient",
        "amount",
        "cause",
        "frequency",
        "is_active",
        "next_due_date",
        "total_donated",
    ]
    list_filter = ["is_active", "frequency"]
    search_fields = ["user__phone", "cause", "recipient__phone"]
