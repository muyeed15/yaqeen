from django.urls import path

from savings.views import (
    MudarabahAccountDetail,
    MudarabahAccountListCreate,
    MudarabahContributionHistory,
    MudarabahPlanList,
    PayMudarabahContribution,
)

urlpatterns = [
    path("mudarabah/plans/", MudarabahPlanList.as_view(), name="mudarabah-plans"),
    path(
        "mudarabah/accounts/",
        MudarabahAccountListCreate.as_view(),
        name="mudarabah-account-list-create",
    ),
    path(
        "mudarabah/accounts/<str:account_number>/",
        MudarabahAccountDetail.as_view(),
        name="mudarabah-account-detail",
    ),
    path(
        "mudarabah/accounts/<str:account_number>/contributions/",
        MudarabahContributionHistory.as_view(),
        name="mudarabah-contribution-history",
    ),
    path(
        "mudarabah/pay/",
        PayMudarabahContribution.as_view(),
        name="mudarabah-pay-contribution",
    ),
]
