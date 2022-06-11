from typing import List, Iterable

from uuid import UUID

from django_redis import get_redis_connection
from rest_framework.renderers import JSONRenderer

from accounts.models import Account

from notifications.models import Notification
from notifications.serializers.notifications import OutputNotificationSerializer


class SendNotificationService:
    connection = get_redis_connection("default")

    def __init__(self, notifications: Iterable[Notification]):
        self._notifications = notifications

    def send(self) -> None:
        data = OutputNotificationSerializer(self._notifications, many=True).data
        payload = JSONRenderer().render(data)
        self.connection.publish("events", payload)


def mark_as_read(notifications_ids: List[UUID], user: Account):
    Notification.objects.filter(to_user=user, id__in=notifications_ids).mark_as_read()
