from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CharityCause, Foundation
from common.utils import (
    credit_wallet,
    error_response,
    list_objects,
    locked_deduct_wallet,
    record_transaction,
    user_objects_or_error,
)

from .models import HawlTracking, Sadaqah, SadaqahJariyah, ZakatPayment
from .serializers import (
    CalculateZakatSerializer,
    CreateSadaqahJariyahSerializer,
    GiveSadaqahSerializer,
    HawlTrackingSerializer,
    PayZakatSerializer,
    SadaqahJariyahSerializer,
    SadaqahSerializer,
    UpdateHawlSerializer,
    ZakatPaymentSerializer,
)


class CalculateZakat(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CalculateZakatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        total_wealth = serializer.validated_data["total_wealth"]
        nisab = serializer.validated_data["nisab_threshold"]

        if total_wealth < nisab:
            return Response(
                {
                    "zakat_due": "0.00",
                    "message": "Wealth is below nisab. No zakat due.",
                    "is_eligible": False,
                }
            )

        zakat_amount = total_wealth * Decimal("0.025")
        return Response(
            {
                "zakat_due": str(zakat_amount.quantize(Decimal("0.01"))),
                "total_wealth": str(total_wealth),
                "nisab_threshold": str(nisab),
                "is_eligible": True,
            }
        )


class PayZakat(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = PayZakatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        recipient_id = serializer.validated_data["recipient_id"]

        foundation = user_objects_or_error(
            Foundation, user_id=recipient_id, is_verified=True
        )
        if foundation is None:
            return error_response("Foundation not found or not verified.")

        wallet = locked_deduct_wallet(request.user, amount)
        if wallet is None:
            return error_response("Insufficient balance")

        credit_wallet(foundation.user, amount)

        payment = ZakatPayment.objects.create(
            user=request.user,
            recipient=foundation.user,
            amount=amount,
            asset_type=serializer.validated_data.get("asset_type", ""),
            hawl_year=serializer.validated_data.get("hawl_year"),
        )

        record_transaction(
            sender=request.user,
            receiver=foundation.user,
            transaction_type="charity",
            amount=amount,
            note=f"Zakat to {foundation.organization_name}",
            counterparty=foundation.organization_name,
            sender_message=(
                f"You paid ৳{amount} Zakat to {foundation.organization_name}."
            ),
        )

        return Response(
            ZakatPaymentSerializer(payment).data, status=status.HTTP_201_CREATED
        )


class ZakatHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return list_objects(ZakatPayment, request.user, ZakatPaymentSerializer)


class GiveSadaqah(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = GiveSadaqahSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        recipient_id = serializer.validated_data["recipient_id"]

        foundation = user_objects_or_error(
            Foundation, user_id=recipient_id, is_verified=True
        )
        if foundation is None:
            return error_response("Foundation not found or not verified.")

        wallet = locked_deduct_wallet(request.user, amount)
        if wallet is None:
            return error_response("Insufficient balance")

        credit_wallet(foundation.user, amount)

        cause_key = serializer.validated_data.get("cause", "")
        cause = (
            CharityCause.objects.filter(key=cause_key).first() if cause_key else None
        )

        donation = Sadaqah.objects.create(
            user=request.user,
            recipient=foundation.user,
            amount=amount,
            cause=cause,
            is_anonymous=serializer.validated_data.get("is_anonymous", False),
        )

        record_transaction(
            sender=request.user,
            receiver=foundation.user,
            transaction_type="charity",
            amount=amount,
            note=f"Sadaqah to {foundation.organization_name}",
            counterparty=foundation.organization_name,
            sender_message=(
                f"You gave ৳{amount} Sadaqah to {foundation.organization_name}."
            ),
        )

        return Response(
            SadaqahSerializer(donation).data, status=status.HTTP_201_CREATED
        )


class SadaqahHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return list_objects(Sadaqah, request.user, SadaqahSerializer)


class HawlTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        haul, _ = HawlTracking.objects.get_or_create(user=request.user)
        return Response(HawlTrackingSerializer(haul).data)

    def post(self, request):
        serializer = UpdateHawlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        haul, _ = HawlTracking.objects.get_or_create(user=request.user)
        current_wealth = serializer.validated_data["current_wealth"]

        if current_wealth >= Decimal("85000") and not haul.is_eligible:
            haul.is_eligible = True
            haul.nisab_crossed_at = timezone.now()
            haul.next_hawl_date = date.today() + relativedelta(months=12)
        elif current_wealth < Decimal("85000"):
            haul.is_eligible = False

        haul.save()
        return Response(HawlTrackingSerializer(haul).data)

    def put(self, request):
        haul, _ = HawlTracking.objects.get_or_create(user=request.user)

        if haul.next_hawl_date and haul.next_hawl_date <= date.today():
            haul.nisab_crossed_at = timezone.now()
            haul.next_hawl_date = date.today() + relativedelta(months=12)
            haul.save()
            return Response(
                {
                    "message": "Hawl renewed. Zakat is due.",
                    "next_hawl_date": haul.next_hawl_date,
                }
            )

        return Response(
            {
                "message": "Hawl period not yet completed.",
                "next_hawl_date": haul.next_hawl_date,
            }
        )


class SadaqahJariyahListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return list_objects(SadaqahJariyah, request.user, SadaqahJariyahSerializer)

    @transaction.atomic
    def post(self, request):
        serializer = CreateSadaqahJariyahSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        recipient_id = serializer.validated_data["recipient_id"]

        foundation = user_objects_or_error(
            Foundation, user_id=recipient_id, is_verified=True
        )
        if foundation is None:
            return error_response("Foundation not found or not verified.")

        wallet = locked_deduct_wallet(request.user, amount)
        if wallet is None:
            return error_response("Insufficient balance for first donation")

        credit_wallet(foundation.user, amount)

        cause_key = serializer.validated_data.get("cause", "")
        cause = (
            CharityCause.objects.filter(key=cause_key).first() if cause_key else None
        )

        donation = SadaqahJariyah.objects.create(
            user=request.user,
            recipient=foundation.user,
            amount=amount,
            cause=cause,
            frequency=serializer.validated_data.get("frequency", "monthly"),
            total_donated=amount,
        )

        record_transaction(
            sender=request.user,
            receiver=foundation.user,
            transaction_type="charity",
            amount=amount,
            note=f"Sadaqah Jariyah to {foundation.organization_name}",
            counterparty=foundation.organization_name,
            sender_message=(
                f"You started a monthly Sadaqah Jariyah of ৳{amount} to "
                f"{foundation.organization_name}."
            ),
        )

        return Response(
            SadaqahJariyahSerializer(donation).data, status=status.HTTP_201_CREATED
        )


class SadaqahJariyahDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, donation_id):
        donation = user_objects_or_error(
            SadaqahJariyah, id=donation_id, user=request.user
        )
        if donation is None:
            return error_response("Donation not found", status.HTTP_404_NOT_FOUND)
        return Response(SadaqahJariyahSerializer(donation).data)

    def patch(self, request, donation_id):
        donation = user_objects_or_error(
            SadaqahJariyah, id=donation_id, user=request.user
        )
        if donation is None:
            return error_response("Donation not found", status.HTTP_404_NOT_FOUND)

        is_active = request.data.get("is_active")
        if is_active is not None:
            donation.is_active = is_active
            donation.save()
            return Response(SadaqahJariyahSerializer(donation).data)

        return error_response("No field to update")
