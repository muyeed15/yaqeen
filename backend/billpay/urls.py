from django.urls import path

from billpay.views import BillerCategoryListView, BillerListView, BillHistoryView, PayBillView

urlpatterns = [
    path("biller-categories/", BillerCategoryListView.as_view(), name="biller-categories"),
    path("billers/", BillerListView.as_view(), name="biller-list"),
    path("pay-bill/", PayBillView.as_view(), name="pay-bill"),
    path("bills/", BillHistoryView.as_view(), name="bill-history"),
]
