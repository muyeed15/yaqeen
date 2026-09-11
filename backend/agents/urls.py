from django.urls import path

from agents.views import (
    AgentDetailView,
    AgentListView,
    AgentTransactionHistoryView,
    CashInView,
    CashOutView,
)

urlpatterns = [
    path("agents/", AgentListView.as_view(), name="agent-list"),
    path("agents/<int:pk>/", AgentDetailView.as_view(), name="agent-detail"),
    path("cash-in/", CashInView.as_view(), name="cash-in"),
    path("cash-out/", CashOutView.as_view(), name="cash-out"),
    path(
        "agent-transactions/",
        AgentTransactionHistoryView.as_view(),
        name="agent-tx-history",
    ),
]
