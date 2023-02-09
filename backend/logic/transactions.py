from typing import List

from backend.helpers.transactions import (
    is_completed_deposit,
    is_completed_scheduled_withdrawal,
    is_refund,
)
from backend.models import (
    Transaction,
    TransactionRow,
    TransactionState,
    TransactionType,
)
from backend.models.interfaces import Database


def get_current_balance(db: Database, user_id: int) -> float:
    """
    Returns the balance of a user.
    """
    balance: int = 0

    for transaction in db.scan("transactions"):
        if transaction.user_id != user_id:
            continue

        if is_completed_deposit(transaction):
            balance += transaction.amount
        elif is_refund(transaction) or is_completed_scheduled_withdrawal(transaction):
            balance -= transaction.amount
    return balance


def transactions(db: Database, user_id: int) -> List[TransactionRow]:
    """
    Returns all transactions of a user.
    """
    return [
        transaction
        for transaction in db.scan("transactions")
        if transaction.user_id == user_id
    ]


def transaction(db: Database, user_id: int, transaction_id: int) -> TransactionRow:
    """
    Returns a given transaction of the user
    """
    transaction = db.get("transactions", transaction_id)
    return transaction if transaction and transaction.user_id == user_id else None


def create_transaction(
    db: Database, user_id: int, transaction: Transaction
) -> TransactionRow:
    """
    Creates a new transaction (adds an ID) and returns it.
    """
    if transaction.type in (TransactionType.DEPOSIT, TransactionType.REFUND):
        initial_state = TransactionState.PENDING
    elif transaction.type == TransactionType.SCHEDULED_WITHDRAWAL:
        initial_state = TransactionState.SCHEDULED
    else:
        raise ValueError(f"Invalid transaction type {transaction.type}")
    transaction_row = TransactionRow(
        user_id=user_id, **transaction.dict(), state=initial_state
    )
    return db.put("transactions", transaction_row)
