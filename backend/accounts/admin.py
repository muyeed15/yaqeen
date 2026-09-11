from django.contrib import admin

from accounts.models import Foundation, KYCVerification, Nominee, OTPVerification, User, Wallet


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone", "full_name", "role", "is_verified", "is_active", "created_at")
    list_filter = ("role", "is_verified", "is_active")
    search_fields = ("phone", "full_name", "nid")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "daily_limit", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__phone", "user__full_name")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Foundation)
class FoundationAdmin(admin.ModelAdmin):
    list_display = ("organization_name", "cause", "is_verified", "user")
    list_filter = ("cause", "is_verified")
    search_fields = ("organization_name", "registration_number")


@admin.register(Nominee)
class NomineeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone", "relationship", "is_primary")
    list_filter = ("relationship", "is_primary")
    search_fields = ("full_name", "phone", "user__phone")


@admin.register(KYCVerification)
class KYCVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "document_type", "document_number", "status", "created_at")
    list_filter = ("document_type", "status")
    search_fields = ("user__phone", "document_number")


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "is_used", "expires_at", "created_at")
    list_filter = ("purpose", "is_used")
    ordering = ("-created_at",)
