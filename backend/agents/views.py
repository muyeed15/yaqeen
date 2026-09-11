import logging
import uuid
from decimal import Decimal

from django.db import transaction
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

from .models import Agent, AgentTransaction
from .serializers import (
    AgentSerializer,
    AgentTransactionSerializer,
    CashInOutSerializer,
)

logger = logging.getLogger("agents")


class AgentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        district = request.query_params.get("district")
        qs = Agent.objects.filter(status="active", is_verified=True)
        if district:
            qs = qs.filter(district__iexact=district)
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": AgentSerializer(p["queryset"], many=True).data,
            }
        )


class AgentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            agent = Agent.objects.get(pk=pk, is_verified=True)
        except Agent.DoesNotExist:
            return error_response("Agent not found.", 404)
        return Response(AgentSerializer(agent).data)


class CashInView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CashInOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent_id = serializer.validated_data["agent_id"]
        amount = serializer.validated_data["amount"]

        try:
            agent = Agent.objects.get(id=agent_id, status="active", is_verified=True)
        except Agent.DoesNotExist:
            return error_response("Agent not found or inactive.")

        commission = (amount * agent.commission_pct / Decimal("100")).quantize(
            Decimal("0.01")
        )
        ref = "CIN" + uuid.uuid4().hex[:10].upper()

        credit_wallet(request.user, amount)

        txn = AgentTransaction.objects.create(
            user=request.user,
            agent=agent,
            amount=amount,
            fee=Decimal("0.00"),
            commission=commission,
            transaction_type="cash_in",
            reference=ref,
            status="completed",
        )

        agent_name = agent.shop_name or agent.full_name
        record_transaction(
            receiver=request.user,
            transaction_type="cash_in",
            amount=amount,
            fee=Decimal("0.00"),
            note=f"Agent cash in at {agent_name}",
            counterparty=agent_name,
            receiver_message=(
                f"You cashed in ৳{amount} via {agent.full_name} at {agent_name}. "
                f"Ref: {ref}"
            ),
        )

        logger.info(
            "CashIn: user=%s agent=%s amount=%s ref=%s",
            request.user.phone,
            agent.phone,
            amount,
            ref,
        )
        return Response(
            AgentTransactionSerializer(txn).data, status=status.HTTP_201_CREATED
        )


class CashOutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CashInOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent_id = serializer.validated_data["agent_id"]
        amount = serializer.validated_data["amount"]

        try:
            agent = Agent.objects.get(id=agent_id, status="active", is_verified=True)
        except Agent.DoesNotExist:
            return error_response("Agent not found or inactive.")

        fee = (amount * Decimal("1.8") / Decimal("100")).quantize(Decimal("0.01"))
        commission = (amount * agent.commission_pct / Decimal("100")).quantize(
            Decimal("0.01")
        )
        total = amount + fee

        wallet = locked_deduct_wallet(request.user, total)
        if wallet is None:
            return error_response("Insufficient balance.")

        ref = "COUT" + uuid.uuid4().hex[:10].upper()
        txn = AgentTransaction.objects.create(
            user=request.user,
            agent=agent,
            amount=amount,
            fee=fee,
            commission=commission,
            transaction_type="cash_out",
            reference=ref,
            status="completed",
        )

        agent_name = agent.shop_name or agent.full_name
        record_transaction(
            sender=request.user,
            transaction_type="cash_out",
            amount=amount,
            fee=fee,
            note=f"Agent cash out at {agent_name}",
            counterparty=agent_name,
            sender_message=(
                f"You cashed out ৳{amount} (fee ৳{fee}) via {agent.full_name} at "
                f"{agent_name}. Ref: {ref}"
            ),
        )

        logger.info(
            "CashOut: user=%s agent=%s amount=%s fee=%s ref=%s",
            request.user.phone,
            agent.phone,
            amount,
            fee,
            ref,
        )
        return Response(
            AgentTransactionSerializer(txn).data, status=status.HTTP_201_CREATED
        )


class AgentTransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            AgentTransaction.objects.filter(user=request.user)
            .select_related("agent")
            .order_by("-created_at")
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": AgentTransactionSerializer(p["queryset"], many=True).data,
            }
        )
