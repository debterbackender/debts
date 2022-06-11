from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from debts import constants
from debts.models import DebtRequest

from notifications.constants import EVENT_CREATED, EVENT_STATUS_UPDATED
from notifications.models import Notification
from notifications.serializers.debts import (
    DebtRequestEventCreatedSerializer,
    DebtRequestEventStatusUpdatedSerializer,
)


debt_request_done = Signal()


@receiver(post_save, sender=DebtRequest)
def notify_request_created(sender, instance: DebtRequest, created: bool, **kwargs):
    if not created:
        return

    if instance.creator == instance.debtor:
        to_user = instance.creditor
    else:
        to_user = instance.debtor

    event_data = DebtRequestEventCreatedSerializer({
        'object': instance,
    }).data
    notification: Notification
    notification = Notification.objects.create(
        event_type=EVENT_CREATED,
        event_data=event_data,
        to_user=to_user,
    )
    notification.send()


@receiver(debt_request_done)
def notify_debt_request_creator(sender: DebtRequest, status: str, **kwargs):
    if status not in (constants.STATUS_ACCEPT, constants.STATUS_DECLINE):
        raise Exception("Status is incorrect!")

    event_data = DebtRequestEventStatusUpdatedSerializer({
        'object': sender,
        'status': status,
    }).data
    notification = Notification.objects.create(
        event_type=EVENT_STATUS_UPDATED,
        event_data=event_data,
        to_user=sender.creator,
    )
    notification.send()
