from django.db.models import QuerySet

from accounts.models import Account
from notifications.models import Notification


def get_all_notifications(user: Account) -> QuerySet[Notification]:
    return Notification.objects.filter(to_user=user).order_by('-created_at')


def get_all_unread_notifications(user: Account) -> QuerySet[Notification]:
    return (
        Notification.objects
            .filter(to_user=user, is_read=False)
            .order_by('-created_by')
    )
