"""Hold normalized receipt data and a reference to its evidence."""

from dataclasses import dataclass
from datetime import date

from expense_report.domain.category import Category
from expense_report.domain.expense_error import ExpenseError
from expense_report.domain.money import Money


@dataclass(frozen=True)
class Receipt:
    """Hold normalized receipt data and a reference to its evidence."""

    receipt_id: str
    vendor: str
    invoice_number: str | None
    spent_on: date
    category: Category
    money: Money
    evidence_reference: str | None

    def __post_init__(self) -> None:
        """Keep invalid receipt identities outside the domain."""
        if not self.receipt_id.strip() or not self.vendor.strip():
            raise ExpenseError("Receipt identifier and vendor are required.")

    def invoice_identity(self) -> tuple[str, str, str] | None:
        """Identify the invoice even if its reported amount has changed."""
        if not self.invoice_number or not self.invoice_number.strip():
            return None

        return (
            self.vendor.strip().casefold(),
            self.invoice_number.strip().casefold(),
            self.money.currency,
        )
