from django.urls import path

from notifications.api import (
    NotificationAPIView,
    UnreadNotificationAPIView,
)

app_name = 'notifications'
urlpatterns = [
    path('', NotificationAPIView.as_view(), name='notifications'),
    path('unread/', UnreadNotificationAPIView.as_view(), name='notifications_unread'),
]
