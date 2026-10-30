"""Represent a positive finite amount with at most two decimal places."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from expense_report.domain.expense_error import ExpenseError


@dataclass(frozen=True)
class Money:
    """Represent a positive finite amount with at most two decimal places."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Reject invalid values instead of silently rounding receipts."""
        if not isinstance(self.amount, Decimal):
            raise ExpenseError("Amounts must use Decimal.")

        if not self.amount.is_finite() or self.amount <= 0:
            raise ExpenseError("Amounts must be finite and positive.")

        try:
            cents = self.amount.quantize(Decimal("0.01"))
        except InvalidOperation as error:
            raise ExpenseError(
                "Amount is outside the supported range."
            ) from error

        if cents != self.amount:
            raise ExpenseError("Amounts must have at most two decimal places.")

        if len(self.currency) != 3 or not self.currency.isascii():
            raise ExpenseError("Currency must be a three-letter code.")
        if not self.currency.isalpha() or not self.currency.isupper():
            raise ExpenseError("Currency must use uppercase letters.")
