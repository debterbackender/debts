import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager

from notifications.constants import EVENTS_TYPE


User = get_user_model()


class NotificationQueryset(models.QuerySet):
    def mark_as_read(self):
        self.update(is_read=True)


class Notification(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=64, choices=EVENTS_TYPE)
    event_data = models.JSONField(default=dict)

    to_user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = Manager.from_queryset(NotificationQueryset)

    def send(self):
        from notifications.services import SendNotificationService

        SendNotificationService([self]).send()
