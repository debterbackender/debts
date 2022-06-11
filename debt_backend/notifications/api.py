from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications import selectors
from notifications.serializers import (
    InputNotificationUpdateReadStatusSerializer,
    OutputNotificationSerializer,
)
from notifications.services import mark_as_read


class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List of all notifications",
        tags=["notifications"],
        responses={
            200: OutputNotificationSerializer(many=True),
        }
    )
    def get(self, request):
        user = request.user
        notifications = selectors.get_all_notifications(user=user)

        serializer = OutputNotificationSerializer(notifications, many=True)
        return Response(data=serializer.data)


class UnreadNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List of unread notifications",
        tags=["notifications"],
        responses={
            200: OutputNotificationSerializer(many=True),
        }
    )
    def get(self, request):
        user = request.user
        notifications = selectors.get_all_unread_notifications(user=user)

        serializer = OutputNotificationSerializer(notifications, many=True)
        return Response(data=serializer.data)

    @swagger_auto_schema(
        operation_description="Mark notifications as read",
        tags=["notifications"],
        request_body=InputNotificationUpdateReadStatusSerializer(),
        responses={
            204: None,
        }
    )
    def patch(self, request):
        user = request.user
        input_serializer = InputNotificationUpdateReadStatusSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        mark_as_read(data['notifications_ids'], user)

        return Response(status=status.HTTP_204_NO_CONTENT)
