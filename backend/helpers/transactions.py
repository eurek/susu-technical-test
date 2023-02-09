from backend.models.interfaces import Database
from backend.models.models import TransactionState, TransactionType


def is_completed_deposit(transaction) -> bool:
    return (
        transaction.type == TransactionType.DEPOSIT
        and transaction.state == TransactionState.COMPLETED
    )


def is_completed_scheduled_withdrawal(transaction) -> bool:
    return (
        transaction.type == TransactionType.SCHEDULED_WITHDRAWAL
        and transaction.state == TransactionState.COMPLETED
    )


def is_refund(transaction) -> bool:
    return transaction.type == TransactionType.REFUND and (
        transaction.state == TransactionState.COMPLETED
        or transaction.state == TransactionState.PENDING
    )
