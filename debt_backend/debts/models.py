import uuid
from typing import Optional

from django.db import models
from django.utils import timezone


class Debt(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    money = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    creditor = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='creditor_debts')
    debtor = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='debtor_debts')
    description = models.TextField(default='', blank=True, null=False)

    created = models.DateTimeField(auto_now_add=True)

    from_request = models.OneToOneField(
        'debts.DebtRequest',
        on_delete=models.SET_NULL,
        null=True,
        related_name='_connected_debt',
        related_query_name='connected_debt',
    )

    closed_request = models.OneToOneField(
        'debts.ClosedDebtRequest',
        on_delete=models.SET_NULL,
        null=True,
        related_name='_from_debt',
        related_query_name='from_debt',
    )

    def is_active(self) -> bool:
        if not self.closed_request:
            return True
        return not self.closed_request.is_closed

    def close_debt(self) -> 'ClosedDebtRequest':
        closed_debt_request, _ = ClosedDebtRequest.objects.get_or_create(
            from_debt=self
        )
        closed_debt_request.close()
        closed_debt_request.refresh_from_db()
        return closed_debt_request

    @classmethod
    def create_from_request(cls, debt_request: 'DebtRequest') -> 'Debt':
        return cls.objects.create(
            money=debt_request.money,
            creditor=debt_request.creditor,
            debtor=debt_request.debtor,
            description=debt_request.description,

            from_request=debt_request,
        )

    def __str__(self) -> str:
        return f"{self.creditor} -> {self.debtor} ({self.money})"


class DebtRequest(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    money = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    creditor = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='creditor_debt_requests',
    )
    debtor = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='debtor_debt_requests',
    )
    creator = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='created_debt_requests',
    )
    description = models.TextField(default='', blank=True, null=False)
    declined = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    @property
    def connected_debt(self) -> Optional[Debt]:
        try:
            return self._connected_debt
        except DebtRequest._connected_debt.RelatedObjectDoesNotExist:  # noqa
            return None

    @connected_debt.setter
    def connected_debt(self, value: Debt) -> None:
        self._connected_debt = value

    @property
    def is_active(self) -> bool:
        return self.connected_debt is None and self.declined is False

    def __str__(self) -> str:
        return f"{self.creditor} -> {self.debtor} ({self.money})"


class ClosedDebtRequest(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    is_closed = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True)
    closed = models.DateTimeField(null=True)

    @property
    def from_debt(self) -> Optional[Debt]:
        try:
            return self._from_debt
        except ClosedDebtRequest._from_debt.RelatedObjectDoesNotExist:
            return None

    @from_debt.setter
    def from_debt(self, value: Debt) -> None:
        self._from_debt = value

    def close(self) -> None:
        self.is_closed = True
        self.closed = timezone.now()
        self.save()
