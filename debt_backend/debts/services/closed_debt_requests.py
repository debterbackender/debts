import uuid

from rest_framework.exceptions import ValidationError

from accounts.models import Account
from debts.models import Debt


class CloseDebtRequestService:
    def __init__(self, debt_id: uuid.UUID, creator: Account):
        self.debt = Debt.objects.get(pk=debt_id)
        self.creator = creator

    def create_close_debt_request(self):
        self._validate_creator_is_related_to_debt()
        if self.creator == self.debt.creditor:
            pass

    def _validate_creator_is_related_to_debt(self):
        if self.creator not in (self.debt.debtor, self.debt.creditor):
            raise ValidationError("User is not debtor/creditor.")
