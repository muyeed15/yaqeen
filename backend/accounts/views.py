import io

import qrcode
from django.db.models import Count
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CharityCause, Foundation, KYCVerification, Nominee, User, Wallet
from accounts.serializers import (
    FoundationSerializer,
    KYCVerificationSerializer,
    NomineeSerializer,
    UserSerializer,
    WalletSerializer,
)
from agents.models import Agent
from common.utils import error_response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallet = Wallet.objects.select_related("user").get(user=request.user)
        except Wallet.DoesNotExist:
            return error_response("Wallet not found.", 404)
        return Response(WalletSerializer(wallet).data)


class NomineeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            NomineeSerializer(Nominee.objects.filter(user=request.user), many=True).data
        )

    def post(self, request):
        serializer = NomineeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get("is_primary"):
            Nominee.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
        nominee = serializer.save(user=request.user)
        return Response(NomineeSerializer(nominee).data, status=status.HTTP_201_CREATED)


class NomineeDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        deleted, _ = Nominee.objects.filter(pk=pk, user=request.user).delete()
        if not deleted:
            return error_response("Nominee not found.", 404)
        return Response(status=status.HTTP_204_NO_CONTENT)


class KYCVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            kyc = KYCVerification.objects.get(user=request.user)
        except KYCVerification.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(KYCVerificationSerializer(kyc).data)

    def put(self, request):
        kyc = KYCVerification.objects.filter(user=request.user).first()
        serializer = KYCVerificationSerializer(kyc, data=request.data)
        serializer.is_valid(raise_exception=True)
        saved = serializer.save(user=request.user, status="pending", verified_at=None)
        return Response(
            KYCVerificationSerializer(saved).data,
            status=status.HTTP_200_OK if kyc else status.HTTP_201_CREATED,
        )


class QRCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        phone = request.user.phone
        data = f"yaqeen://pay/{phone}"

        img = qrcode.make(data, box_size=10, border=2)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return HttpResponse(
            buf.getvalue(),
            content_type="image/png",
            headers={
                "Cache-Control": "no-cache",
                "Content-Disposition": f'inline; filename="qr-{phone}.png"',
            },
        )


class PhoneLookupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, phone):
        try:
            user = User.objects.get(phone=phone, is_active=True)
        except User.DoesNotExist:
            try:
                agent = Agent.objects.get(phone=phone, is_verified=True, status="active")
            except Agent.DoesNotExist:
                return error_response("No account found with this phone number.", 404)
            return Response(
                {
                    "phone": agent.phone,
                    "full_name": agent.full_name,
                    "name": agent.shop_name,
                    "type": "agent",
                    "is_verified_merchant": False,
                }
            )

        merchant = getattr(user, "merchant_profile", None)
        is_verified_merchant = bool(merchant and merchant.is_verified)
        return Response(
            {
                "phone": user.phone,
                "full_name": user.full_name,
                "name": merchant.business_name if is_verified_merchant else user.full_name,
                "type": "merchant" if is_verified_merchant else "user",
                "is_verified_merchant": is_verified_merchant,
            }
        )


class FoundationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cause = request.query_params.get("cause")
        foundations = Foundation.objects.filter(is_verified=True).select_related("user", "cause")
        if cause:
            foundations = foundations.filter(cause__key=cause)
        serializer = FoundationSerializer(foundations, many=True, context={"request": request})
        return Response(serializer.data)


class FoundationCauseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        counts = (
            Foundation.objects.filter(is_verified=True)
            .values("cause__key")
            .annotate(count=Count("id"))
        )
        counts_by_cause = {c["cause__key"]: c["count"] for c in counts}
        causes = [
            {
                "key": cause.key,
                "label": cause.label,
                "icon": cause.icon,
                "count": counts_by_cause.get(cause.key, 0),
            }
            for cause in CharityCause.objects.filter(is_active=True)
        ]
        return Response(causes)


class FoundationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            foundation = Foundation.objects.select_related("user", "cause").get(
                pk=pk, is_verified=True
            )
        except Foundation.DoesNotExist:
            return error_response("Foundation not found.", 404)
        return Response(FoundationSerializer(foundation, context={"request": request}).data)
