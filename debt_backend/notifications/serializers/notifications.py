from typing import Iterable

from rest_framework import serializers

from notifications import constants
from notifications.models import Notification
from notifications.serializers import debts as debts_serializers


class EventDataSerializer(serializers.Serializer):
    EVENT_TYPES = {
        constants.EVENT_CREATED: debts_serializers.DebtRequestEventCreatedSerializer(),
        constants.EVENT_STATUS_UPDATED: debts_serializers.DebtRequestEventStatusUpdatedSerializer(),
    }
    def to_representation(self, instance):
        self.parent: OutputNotificationSerializer
        notification = self.parent.instance

        # in case if parent serializer uses .many_init()
        # (for e.x. serializer initialized with many=True)
        if isinstance(notification, Iterable):
            notification = notification[0]

        serializer = self.EVENT_TYPES[notification.event_type]
        return serializer.to_representation(instance)


class OutputNotificationSerializer(serializers.ModelSerializer):
    event_data = EventDataSerializer()

    class Meta:
        model = Notification
        fields = [
            'id', 'event_type', 'event_data',
            'is_read', 'to_user', 'created_at',
        ]


class InputNotificationUpdateReadStatusSerializer(serializers.Serializer):
    notifications_ids = serializers.ListField(child=serializers.UUIDField())
