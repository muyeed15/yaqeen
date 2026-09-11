from django.urls import path

from statements.views import GenerateStatementView, StatementListView

urlpatterns = [
    path("statements/", StatementListView.as_view(), name="statement-list"),
    path("statements/generate/", GenerateStatementView.as_view(), name="statement-generate"),
]
