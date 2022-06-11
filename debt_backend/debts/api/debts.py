from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q

from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account
from debts import selectors
from debts.models import Debt
from debts.serializers import OutputDebtSerializer
from debts.services import CreateClosedDebtRequestService


class DebtAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List of debts",
        tags=["debts"],
        responses={
            200: OutputDebtSerializer(many=True),
        }
    )
    def get(self, request):
        user: Account = request.user
        debts = selectors.get_related_debts(user)

        result = OutputDebtSerializer(debts, many=True).data
        return Response(data=result)


class DetailDebtApiView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Detail debt",
        tags=["debts"],
        responses={
            200: OutputDebtSerializer(),
        }
    )
    def get(self, request, pk):
        user = request.user
        debt = get_object_or_404(
            Debt.objects.filter(
                Q(creditor=user) | Q(debtor=user)
            ), pk=pk,
        )

        result = OutputDebtSerializer(debt).data
        return Response(data=result)

    @swagger_auto_schema(
        operation_description="Close debt",
        tags=["debts"],
        responses={
            201: None,
        }
    )
    def close_debt(self, request, pk):
        service = CreateClosedDebtRequestService(debt_id=pk, creator=request.user)
        service.create_close_debt_request()

        return Response(status=status.HTTP_201_CREATED)
