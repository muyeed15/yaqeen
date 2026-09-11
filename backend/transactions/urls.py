from django.urls import path

from transactions.views import (
    CreateMoneyRequestView,
    MoneyRequestListView,
    RespondMoneyRequestView,
    TransactionDetailView,
    TransactionListView,
    TransferView,
)

urlpatterns = [
    path("transfer/", TransferView.as_view(), name="transfer"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path("transactions/<int:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("money-requests/", MoneyRequestListView.as_view(), name="money-request-list"),
    path("money-requests/create/", CreateMoneyRequestView.as_view(), name="money-request-create"),
    path(
        "money-requests/<int:pk>/respond/",
        RespondMoneyRequestView.as_view(),
        name="money-request-respond",
    ),
]
