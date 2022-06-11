from django.contrib.auth import get_user_model
from rest_framework import serializers

from debts.models import DebtRequest, Debt
from debts import constants as debts_constants


User = get_user_model()


class ShortNotificationDebtSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default=Debt.__name__)

    class Meta:
        model = Debt
        fields = [
            'id', 'type', 'is_active',
        ]


class NotificationAccountSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    username = serializers.CharField()
    type = serializers.CharField(default=User.__name__)

    class Meta:
        model = User
        fields = [
            'id', 'type', 'username',
        ]


class NotificationDebtRequestSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default=DebtRequest.__name__)
    debtor = NotificationAccountSerializer()
    creditor = NotificationAccountSerializer()
    is_active = serializers.BooleanField()
    connected_debt = ShortNotificationDebtSerializer(allow_null=True)

    class Meta:
        model = DebtRequest
        fields = [
            'id', 'money', 'creditor',
            'type', 'debtor', 'description',
            'created', 'is_active', 'connected_debt',
        ]


class DebtRequestEventCreatedSerializer(serializers.Serializer):
    object = NotificationDebtRequestSerializer()


class DebtRequestEventStatusUpdatedSerializer(serializers.Serializer):
    object = NotificationDebtRequestSerializer()
    status = serializers.ChoiceField(debts_constants.DEBT_REQUEST_STATUS)
