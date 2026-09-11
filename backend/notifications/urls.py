from django.urls import path

from notifications.views import (
    NotificationDetailView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationStreamView,
)

urlpatterns = [
    path(
        "notifications/stream/",
        NotificationStreamView.as_view(),
        name="notification-stream",
    ),
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/read-all/",
        NotificationMarkAllReadView.as_view(),
        name="notification-read-all",
    ),
    path(
        "notifications/<int:pk>/",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),
]
