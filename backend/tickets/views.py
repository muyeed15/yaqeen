import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page, get_page_size, paginate
from common.utils import (
    credit_wallet,
    error_response,
    locked_deduct_wallet,
    record_transaction,
)

from .models import TicketBooking, TicketCategory, TicketProvider, TicketTrip
from .serializers import (
    BookTicketSerializer,
    TicketBookingSerializer,
    TicketProviderSerializer,
    TicketTripSerializer,
)

logger = logging.getLogger("tickets")


class TicketCategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        counts = (
            TicketProvider.objects.filter(is_active=True)
            .values("category__key")
            .annotate(count=Count("id"))
        )
        counts_by_category = {c["category__key"]: c["count"] for c in counts}
        categories = [
            {
                "key": category.key,
                "label": category.label,
                "count": counts_by_category.get(category.key, 0),
            }
            for category in TicketCategory.objects.filter(is_active=True)
        ]
        return Response(categories)


class TicketProviderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get("category")
        qs = (
            TicketProvider.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("trips")
        )
        if category:
            qs = qs.filter(category__key=category)
        return Response(
            TicketProviderSerializer(qs, many=True, context={"request": request}).data
        )


class TicketTripsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        provider_id = request.query_params.get("provider_id")
        qs = TicketTrip.objects.filter(is_active=True)
        if provider_id:
            qs = qs.filter(provider_id=provider_id)
        return Response(TicketTripSerializer(qs, many=True).data)


class BookTicketView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = BookTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider_id = serializer.validated_data["provider_id"]
        passengers = serializer.validated_data["passengers"]

        try:
            provider = TicketProvider.objects.get(id=provider_id, is_active=True)
        except TicketProvider.DoesNotExist:
            return error_response("Ticket provider not found or inactive.")

        trip_id = serializer.validated_data.get("trip_id")
        trip = None
        if trip_id:
            try:
                trip = TicketTrip.objects.get(id=trip_id, provider=provider)
            except TicketTrip.DoesNotExist:
                return error_response("Trip not found.")

        # When a trip is selected, the total is derived from its price and the
        # passenger count so the client cannot submit an arbitrary amount.
        if trip is not None:
            amount = (trip.price * passengers).quantize(Decimal("0.01"))
        else:
            amount = serializer.validated_data["amount"]

        wallet = locked_deduct_wallet(request.user, amount)
        if wallet is None:
            return error_response("Insufficient balance.")

        booking = TicketBooking.objects.create(
            user=request.user,
            provider=provider,
            journey_date=serializer.validated_data["journey_date"],
            departure_time=serializer.validated_data.get("departure_time", ""),
            origin=serializer.validated_data.get("origin", ""),
            destination=serializer.validated_data.get("destination", ""),
            trip_name=serializer.validated_data.get("trip_name", ""),
            coach_class=serializer.validated_data.get("coach_class", ""),
            coach=serializer.validated_data.get("coach", ""),
            seat_number=serializer.validated_data.get("seat_number", ""),
            passengers=serializer.validated_data["passengers"],
            amount=amount,
            status="confirmed",
        )

        route = (
            " to ".join(part for part in (booking.origin, booking.destination) if part)
            or booking.trip_name
        )
        record_transaction(
            sender=request.user,
            transaction_type="ticket",
            amount=amount,
            note=f"{provider.name} ticket {route}".strip(),
            counterparty=provider.name,
            sender_message=(
                f"You booked a {provider.name} ticket for ৳{amount}. "
                f"Ref: {booking.booking_reference}"
            ),
        )

        logger.info(
            "BookTicket: user=%s provider=%s route=%s->%s date=%s amount=%s ref=%s",
            request.user.phone,
            provider.name,
            booking.origin,
            booking.destination,
            booking.journey_date,
            amount,
            booking.booking_reference,
        )
        return Response(
            TicketBookingSerializer(booking).data, status=status.HTTP_201_CREATED
        )


class TicketHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            TicketBooking.objects.filter(user=request.user)
            .select_related("provider")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": TicketBookingSerializer(p["queryset"], many=True).data,
            }
        )


class CancelTicketView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            booking = TicketBooking.objects.get(pk=pk, user=request.user)
        except TicketBooking.DoesNotExist:
            return error_response("Booking not found.", 404)

        if booking.status != "confirmed":
            return error_response("Only confirmed bookings can be cancelled.")

        refund = (booking.amount * Decimal("0.70")).quantize(Decimal("0.01"))

        credit_wallet(request.user, refund)

        booking.status = "refunded"
        booking.save(update_fields=["status"])

        record_transaction(
            receiver=request.user,
            transaction_type="ticket",
            amount=refund,
            note=f"Refund for booking {booking.booking_reference}",
            counterparty=booking.provider.name,
            receiver_message=(
                f"Refund of ৳{refund} credited for booking {booking.booking_reference}."
            ),
        )

        logger.info(
            "CancelTicket: user=%s ref=%s refund=%s",
            request.user.phone,
            booking.booking_reference,
            refund,
        )
        return Response(
            {
                "message": f"Booking {booking.booking_reference} cancelled. Refund of ৳{refund} credited."
            }
        )
