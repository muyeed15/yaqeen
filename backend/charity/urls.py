from django.urls import path

from charity.views import (
    CalculateZakat,
    GiveSadaqah,
    HawlTrackingView,
    PayZakat,
    SadaqahHistory,
    SadaqahJariyahDetail,
    SadaqahJariyahListCreate,
    ZakatHistory,
)

urlpatterns = [
    path("zakat/calculate/", CalculateZakat.as_view(), name="zakat-calculate"),
    path("zakat/pay/", PayZakat.as_view(), name="zakat-pay"),
    path("zakat/history/", ZakatHistory.as_view(), name="zakat-history"),
    path("sadaqah/", GiveSadaqah.as_view(), name="sadaqah-give"),
    path("sadaqah/history/", SadaqahHistory.as_view(), name="sadaqah-history"),
    path("hawl/", HawlTrackingView.as_view(), name="hawl-tracking"),
    path(
        "sadaqah-jariyah/", SadaqahJariyahListCreate.as_view(), name="sadaqah-jariyah-list-create"
    ),
    path(
        "sadaqah-jariyah/<int:donation_id>/",
        SadaqahJariyahDetail.as_view(),
        name="sadaqah-jariyah-detail",
    ),
]
