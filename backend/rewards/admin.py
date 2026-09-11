from django.contrib import admin

from .models import Offer, PointsTransaction, Reward, UserOffer


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ["user", "points", "lifetime_points"]
    search_fields = ["user__phone"]


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "points", "transaction_type", "reason", "created_at"]
    list_filter = ["transaction_type"]
    ordering = ["-created_at"]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "points_required",
        "cashback_amount",
        "valid_from",
        "valid_until",
        "is_active",
    ]
    list_filter = ["is_active", "category"]


@admin.register(UserOffer)
class UserOfferAdmin(admin.ModelAdmin):
    list_display = ["user", "offer", "is_claimed", "claimed_at"]
    list_filter = ["is_claimed"]
