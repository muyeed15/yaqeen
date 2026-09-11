from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from common.tests.helpers import make_user
from notifications.models import Notification


class NotificationListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)
        for i in range(3):
            Notification.objects.create(user=self.user, message=f"Notification {i}")

    def test_list_notifications(self):
        res = self.client.get("/api/notifications/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 3)

    def test_list_only_own_notifications(self):
        other = make_user("01700000002", "2222222222")
        Notification.objects.create(user=other, message="Other's notification")
        res = self.client.get("/api/notifications/")
        self.assertEqual(res.data["count"], 3)

    def test_list_paginated(self):
        res = self.client.get("/api/notifications/")
        self.assertIn("count", res.data)
        self.assertIn("results", res.data)

    def test_unauthenticated(self):
        self.client.force_authenticate(user=None)
        res = self.client.get("/api/notifications/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class NotificationDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.notification = Notification.objects.create(
            user=self.user,
            message="Test notification",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_detail(self):
        res = self.client.get(f"/api/notifications/{self.notification.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "Test notification")

    def test_mark_as_read(self):
        res = self.client.patch(f"/api/notifications/{self.notification.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_mark_already_read(self):
        self.notification.is_read = True
        self.notification.save()
        res = self.client.patch(f"/api/notifications/{self.notification.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_other_users_notification(self):
        other = make_user("01700000002", "2222222222")
        other_notif = Notification.objects.create(user=other, message="Secret")
        res = self.client.get(f"/api/notifications/{other_notif.pk}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent(self):
        res = self.client.get("/api/notifications/9999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class NotificationMarkAllReadViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        for i in range(3):
            Notification.objects.create(user=self.user, message=f"Note {i}")
        self.client.force_authenticate(user=self.user)

    def test_mark_all_read(self):
        res = self.client.post("/api/notifications/read-all/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["marked_read"], 3)
        self.assertEqual(Notification.objects.filter(is_read=True).count(), 3)

    def test_mark_all_read_when_none_unread(self):
        Notification.objects.all().update(is_read=True)
        res = self.client.post("/api/notifications/read-all/")
        self.assertEqual(res.data["marked_read"], 0)


class NotificationStreamViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.default_format = "json"
        self.user = make_user("01700000001", "1111111111")
        self.client.force_authenticate(user=self.user)

    def test_stream_returns_event_stream_content_type(self):
        res = self.client.get("/api/notifications/stream/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res["Content-Type"], "text/event-stream")

    def test_stream_with_last_id(self):
        Notification.objects.create(user=self.user, message="Old")
        Notification.objects.create(user=self.user, message="New")
        res = self.client.get("/api/notifications/stream/?last_id=1")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_stream_invalid_last_id_ignored(self):
        res = self.client.get("/api/notifications/stream/?last_id=abc")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_empty_notification_list(self):
        Notification.objects.all().delete()
        res = self.client.get("/api/notifications/")
        self.assertEqual(res.data["count"], 0)
        self.assertEqual(res.data["results"], [])

    def test_notification_pagination(self):
        for i in range(15):
            Notification.objects.create(user=self.user, message=f"Bulk {i}")
        res = self.client.get("/api/notifications/")
        self.assertEqual(res.data["count"], 15)
        self.assertEqual(len(res.data["results"]), 10)
