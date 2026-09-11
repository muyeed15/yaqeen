from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import (
    error_response,
    list_objects,
    locked_deduct_wallet,
    record_transaction,
    user_objects_or_error,
)

from .models import MudarabahAccount, MudarabahContribution, MudarabahPlan
from .serializers import (
    MudarabahAccountSerializer,
    MudarabahContributionSerializer,
    MudarabahPlanSerializer,
    PayContributionSerializer,
)


class MudarabahPlanList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = MudarabahPlan.objects.filter(is_active=True)
        return Response(MudarabahPlanSerializer(plans, many=True).data)


class MudarabahAccountListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return list_objects(MudarabahAccount, request.user, MudarabahAccountSerializer)

    @transaction.atomic
    def post(self, request):
        plan_id = request.data.get("plan_id")
        try:
            plan = MudarabahPlan.objects.get(id=plan_id, is_active=True)
        except MudarabahPlan.DoesNotExist:
            return error_response("Invalid or inactive plan")

        wallet = locked_deduct_wallet(request.user, plan.monthly_amount)
        if wallet is None:
            return error_response("Insufficient balance for first contribution")

        account = MudarabahAccount.objects.create(user=request.user, plan=plan)
        MudarabahContribution.objects.create(
            mudarabah_account=account,
            installment_number=1,
            amount=plan.monthly_amount,
        )
        account.total_deposited = plan.monthly_amount
        account.update_expected_payout()
        account.save()

        record_transaction(
            sender=request.user,
            transaction_type="savings",
            amount=plan.monthly_amount,
            note=f"{plan.name} installment 1",
            counterparty=plan.name,
            sender_message=(
                f"You paid ৳{plan.monthly_amount} as the first contribution to " f"{plan.name}."
            ),
        )

        return Response(MudarabahAccountSerializer(account).data, status=status.HTTP_201_CREATED)


class MudarabahAccountDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_number):
        account = user_objects_or_error(
            MudarabahAccount,
            account_number=account_number,
            user=request.user,
        )
        if account is None:
            return error_response("Account not found", status.HTTP_404_NOT_FOUND)
        return Response(MudarabahAccountSerializer(account).data)


class MudarabahContributionHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_number):
        account = user_objects_or_error(
            MudarabahAccount,
            account_number=account_number,
            user=request.user,
        )
        if account is None:
            return error_response("Account not found", status.HTTP_404_NOT_FOUND)
        contributions = MudarabahContribution.objects.filter(mudarabah_account=account)
        return Response(MudarabahContributionSerializer(contributions, many=True).data)


class PayMudarabahContribution(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = PayContributionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account = user_objects_or_error(
            MudarabahAccount,
            account_number=serializer.validated_data["account_number"],
            user=request.user,
            status="active",
        )
        if account is None:
            return error_response("Active account not found", status.HTTP_404_NOT_FOUND)

        amount = serializer.validated_data["amount"]

        last_contribution = (
            MudarabahContribution.objects.filter(mudarabah_account=account)
            .order_by("-installment_number")
            .first()
        )
        next_number = (last_contribution.installment_number + 1) if last_contribution else 1

        if next_number > account.plan.duration_months:
            return error_response("All contributions already paid")

        wallet = locked_deduct_wallet(request.user, amount)
        if wallet is None:
            return error_response("Insufficient balance")

        MudarabahContribution.objects.create(
            mudarabah_account=account,
            installment_number=next_number,
            amount=amount,
        )
        account.total_deposited += amount
        account.update_expected_payout()
        account.save()

        record_transaction(
            sender=request.user,
            transaction_type="savings",
            amount=amount,
            note=f"{account.plan.name} installment {next_number}",
            counterparty=account.plan.name,
            sender_message=(
                f"You paid ৳{amount} for {account.plan.name} installment " f"#{next_number}."
            ),
        )

        if next_number == account.plan.duration_months:
            account.status = "matured"
            account.save()

        return Response({"message": f"Contribution #{next_number} paid successfully"})
