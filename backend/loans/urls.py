from django.urls import path

from loans.views import (
    ApplyQardHasanView,
    QardHasanDetailView,
    QardHasanListView,
    QardHasanProductListView,
    RepayQardHasanView,
)

urlpatterns = [
    path(
        "qard-hasan-products/",
        QardHasanProductListView.as_view(),
        name="qard-hasan-product-list",
    ),
    path("apply-qard-hasan/", ApplyQardHasanView.as_view(), name="apply-qard-hasan"),
    path("qard-hasan/", QardHasanListView.as_view(), name="qard-hasan-list"),
    path(
        "qard-hasan/<int:pk>/", QardHasanDetailView.as_view(), name="qard-hasan-detail"
    ),
    path(
        "qard-hasan/<int:pk>/repay/",
        RepayQardHasanView.as_view(),
        name="repay-qard-hasan",
    ),
]
