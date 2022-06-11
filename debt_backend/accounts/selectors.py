from django.db.models import QuerySet

from accounts.models import Account, FriendRequest


def get_friend_requests_to_accept(user: Account) -> QuerySet[FriendRequest]:
    return user.friend_requests.order_by('-created_at').select_related('to_user')
