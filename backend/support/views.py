import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import error_response, user_objects_or_error

from .models import SupportCategory, SupportTicket, TicketMessage
from .serializers import (
    CreateTicketSerializer,
    SupportTicketSerializer,
    TicketReplySerializer,
)

logger = logging.getLogger("support")


class SupportCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = [
            {"key": c.key, "label": c.label}
            for c in SupportCategory.objects.filter(is_active=True)
        ]
        return Response(categories)


class TicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = (
            SupportTicket.objects.filter(user=request.user)
            .select_related("category")
            .prefetch_related("messages")
            .order_by("-created_at")
        )
        return Response(SupportTicketSerializer(tickets, many=True).data)

    def post(self, request):
        serializer = CreateTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category_key = serializer.validated_data.get("category", "")
        category = (
            SupportCategory.objects.filter(key=category_key).first()
            if category_key
            else None
        )

        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=serializer.validated_data["subject"],
            category=category,
        )

        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=serializer.validated_data["message"],
        )

        logger.info(
            "New ticket: user=%s subject=%s", request.user.phone, ticket.subject
        )
        return Response(
            SupportTicketSerializer(ticket).data, status=status.HTTP_201_CREATED
        )


class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        ticket = user_objects_or_error(SupportTicket, id=pk, user=request.user)
        if ticket is None:
            return error_response("Ticket not found.", 404)
        return Response(SupportTicketSerializer(ticket).data)


class TicketReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ticket = user_objects_or_error(SupportTicket, id=pk, user=request.user)
        if ticket is None:
            return error_response("Ticket not found.", 404)

        if ticket.status in ("closed", "resolved"):
            return error_response("Cannot reply to a closed ticket.")

        serializer = TicketReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=serializer.validated_data["message"],
        )

        ticket.status = "in_progress"
        ticket.save(update_fields=["status"])

        return Response(SupportTicketSerializer(ticket).data)
