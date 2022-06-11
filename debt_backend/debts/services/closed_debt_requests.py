import uuid

from rest_framework.exceptions import ValidationError

from accounts.models import Account
from debts.models import Debt, ClosedDebtRequest


class CreateClosedDebtRequestService:
    def __init__(self, debt_id: uuid.UUID, creator: Account):
        self.debt = Debt.objects.get(pk=debt_id)
        self.creator = creator

    def create_close_debt_request(self) -> ClosedDebtRequest:
        if self.creator.id == self.debt.creditor_id:
            return self.close_as_creditor()
        elif self.creator.id == self.debt.debtor_id:
            return self.close_as_creditor()
        else:
            raise ValidationError("User is not debtor/creditor.")

    def close_as_creditor(self):
        return self.debt.close_debt()

    def close_as_debtor(self):
        closed_request = ClosedDebtRequest.objects.create(from_debt=self.debt)
        self.debt.closed_request = closed_request
        self.debt.save()
        return closed_request
