import logging
from decimal import Decimal

from django.db.models import Q, Sum
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import get_page, get_page_size, paginate
from common.utils import error_response
from transactions.models import Transaction

from .models import AccountStatement
from .serializers import GenerateStatementSerializer, StatementSerializer

logger = logging.getLogger("statements")


class StatementListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = AccountStatement.objects.filter(user=request.user).order_by(
            "-year", "-month"
        )
        p = paginate(qs, get_page(request), get_page_size(request))
        return Response(
            {
                "count": p["count"],
                "total_pages": p["total_pages"],
                "page": p["page"],
                "results": StatementSerializer(p["queryset"], many=True).data,
            }
        )


class GenerateStatementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateStatementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        year = serializer.validated_data["year"]
        month = serializer.validated_data["month"]

        existing = AccountStatement.objects.filter(
            user=request.user, year=year, month=month
        ).first()
        if existing:
            return Response(StatementSerializer(existing).data)

        txns = Transaction.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            created_at__year=year,
            created_at__month=month,
        )

        credits = txns.filter(receiver=request.user, status="completed").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")
        debits = txns.filter(sender=request.user, status="completed").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")

        if not txns.exists():
            return error_response("No transactions found for this period.")

        wallet = request.user.wallet
        opening = wallet.balance - credits + debits
        closing = wallet.balance

        statement = AccountStatement.objects.create(
            user=request.user,
            year=year,
            month=month,
            opening_balance=opening,
            closing_balance=closing,
            total_credits=credits,
            total_debits=debits,
            transaction_count=txns.count(),
        )

        return Response(
            StatementSerializer(statement).data, status=status.HTTP_201_CREATED
        )
