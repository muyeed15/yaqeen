from django.contrib import admin

from .models import TicketBooking, TicketCategory, TicketProvider


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ["key", "label", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["key", "label"]


@admin.register(TicketProvider)
class TicketProviderAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_active"]
    list_filter = ["category", "is_active"]


@admin.register(TicketBooking)
class TicketBookingAdmin(admin.ModelAdmin):
    list_display = [
        "booking_reference",
        "user",
        "provider",
        "origin",
        "destination",
        "amount",
        "status",
        "created_at",
    ]
    list_filter = ["status", "provider"]
    search_fields = ["booking_reference", "user__phone"]
    ordering = ["-created_at"]
