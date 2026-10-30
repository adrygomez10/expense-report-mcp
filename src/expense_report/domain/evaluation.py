"""Partition EUR totals while retaining unconverted foreign receipts."""

from dataclasses import dataclass
from decimal import Decimal

from expense_report.domain.assessment import Assessment
from expense_report.domain.decision import Decision
from expense_report.domain.trip import Trip


@dataclass(frozen=True)
class Evaluation:
    """Partition EUR totals while retaining unconverted foreign receipts."""

    trip: Trip
    policy_version: str
    assessments: tuple[Assessment, ...]

    def total(self, decision: Decision | None = None) -> Decimal:
        """Sum only EUR values, optionally restricting the decision."""
        total = Decimal("0.00")
        for assessment in self.assessments:
            if assessment.receipt.money.currency != "EUR":
                continue
            if decision is not None and assessment.decision != decision:
                continue

            total += assessment.receipt.money.amount

        return total
