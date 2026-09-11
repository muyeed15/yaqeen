import json
import logging
import time

from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page, get_page_size, paginate
from common.utils import error_response
from notifications.models import Notification
from notifications.serializers import NotificationSerializer

logger = logging.getLogger("notifications")


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            Notification.objects.filter(user=request.user)
            .only("id", "message", "is_read", "created_at")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": NotificationSerializer(p["queryset"], many=True).data,
            }
        )


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_notification(self, user, pk):
        try:
            return (
                Notification.objects.filter(user=user)
                .only("id", "message", "is_read", "created_at")
                .get(pk=pk)
            )
        except Notification.DoesNotExist:
            return None

    def get(self, request, pk):
        notification = self._get_notification(request.user, pk)
        if notification is None:
            return error_response("Not found.", 404)
        return Response(NotificationSerializer(notification).data)

    def patch(self, request, pk):
        notification = self._get_notification(request.user, pk)
        if notification is None:
            return error_response("Not found.", 404)

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])

        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True
        )
        return Response({"marked_read": updated})


class NotificationStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            last_id = int(request.GET.get("last_id", 0))
        except (ValueError, TypeError):
            last_id = 0

        user = request.user

        def event_stream():
            nonlocal last_id
            logger.info("SSE connected for user=%s last_id=%s", user.phone, last_id)
            yield ": connected\n\n"
            last_heartbeat = time.time()
            try:
                while True:
                    try:
                        new = list(
                            Notification.objects.filter(user=user, id__gt=last_id)
                            .order_by("id")
                            .values("id", "message", "is_read", "created_at")
                        )
                    except Exception as e:
                        logger.error("SSE query error for user=%s: %s", user.phone, e)
                        yield f"event: error\ndata: {json.dumps({'detail': 'Query failed'})}\n\n"
                        time.sleep(5)
                        continue

                    for notif in new:
                        last_id = notif["id"]
                        payload = json.dumps(
                            {
                                "id": notif["id"],
                                "message": notif["message"],
                                "is_read": notif["is_read"],
                                "created_at": notif["created_at"].isoformat(),
                            }
                        )
                        yield f"event: notification\ndata: {payload}\n\n"

                    now = time.time()
                    if now - last_heartbeat >= 15:
                        yield ": heartbeat\n\n"
                        last_heartbeat = now

                    time.sleep(2)
            except GeneratorExit:
                logger.info("SSE disconnected for user=%s", user.phone)

        response = StreamingHttpResponse(
            event_stream(), content_type="text/event-stream"
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
