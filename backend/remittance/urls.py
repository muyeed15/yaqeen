from django.urls import path

from remittance.views import (
    PartnerListView,
    ReceiveRemittanceView,
    RemittanceHistoryView,
)

urlpatterns = [
    path(
        "remittance-partners/",
        PartnerListView.as_view(),
        name="remittance-partner-list",
    ),
    path(
        "receive-remittance/",
        ReceiveRemittanceView.as_view(),
        name="receive-remittance",
    ),
    path("remittances/", RemittanceHistoryView.as_view(), name="remittance-history"),
]
