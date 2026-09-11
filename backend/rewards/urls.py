from django.urls import path

from rewards.views import ClaimOfferView, OfferListView, PointsHistoryView, RewardView

urlpatterns = [
    path("rewards/", RewardView.as_view(), name="rewards"),
    path("points-history/", PointsHistoryView.as_view(), name="points-history"),
    path("offers/", OfferListView.as_view(), name="offer-list"),
    path("offers/<int:pk>/claim/", ClaimOfferView.as_view(), name="claim-offer"),
]
