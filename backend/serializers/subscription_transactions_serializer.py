from typing import List

from backend.logic.transactions import get_current_balance

from backend.models.models import (
    SubscriptionTransaction,
    TransactionRow,
    TransactionState,
    TransactionType,
)


class SubscriptionTransactionsSerializer:
    """
    Returns next scheduled withdrawal balance of an User.
    """

    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    def call(self):
        next_user_subscription_transactions: SubscriptionTransaction = []
        current_balance: float = get_current_balance(self.db, self.user_id)

        for transaction in self._get_next_scheduled_withdrawal():
            next_user_subscription_transactions.append(
                {
                    "amount": transaction.amount,
                    "coverage_amount": self._get_coverage_amount(
                        transaction.amount, current_balance
                    ),
                    "date": transaction.date,
                    "rate_coverage_amount": self._get_rate_coverage_amount(
                        transaction.amount, current_balance
                    ),
                }
            )

            current_balance -= transaction.amount

        return next_user_subscription_transactions

    def _get_coverage_amount(self, amount, balance) -> int:
        if balance < 0:
            return 0

        return amount if balance > amount else balance

    def _get_next_scheduled_withdrawal(self) -> List[TransactionRow]:
        return [
            transaction
            for transaction in self.db.scan("transactions")
            if transaction.type == TransactionType.SCHEDULED_WITHDRAWAL
            and transaction.user_id == self.user_id
            and transaction.state == TransactionState.SCHEDULED
        ]

    def _get_rate_coverage_amount(self, amount, balance) -> int:
        rate = balance / amount

        if rate >= 1:
            rate = 100
        elif rate <= 0:
            rate = 0
        else:
            rate = round(rate * 100, 1)

        return rate
