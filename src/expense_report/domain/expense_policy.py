"""Apply the fictional company's explicit EUR expense policy."""

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from expense_report.domain.assessment import Assessment
from expense_report.domain.category import Category
from expense_report.domain.decision import Decision
from expense_report.domain.evaluation import Evaluation
from expense_report.domain.expense_error import ExpenseError
from expense_report.domain.money import Money
from expense_report.domain.receipt import Receipt
from expense_report.domain.trip import Trip


@dataclass(frozen=True)
class ExpensePolicy:
    """Apply the fictional company's explicit EUR expense policy."""

    version: str = "demo-2026-10"
    hotel_per_receipt: Decimal = Decimal("180.00")
    meals_per_day: Decimal = Decimal("35.00")

    def __post_init__(self) -> None:
        """Reject empty versions and invalid monetary policy limits."""
        if not self.version.strip():
            raise ExpenseError("Policy version is required.")

        Money(amount=self.hotel_per_receipt, currency="EUR")
        Money(amount=self.meals_per_day, currency="EUR")

    def evaluate(self, trip: Trip, receipts: Sequence[Receipt]) -> Evaluation:
        """Exclude repeated invoices, then assess the unique receipt set."""
        identities = [receipt.receipt_id for receipt in receipts]
        if len(set(identities)) != len(identities):
            raise ExpenseError("Receipt identifiers must be unique.")

        duplicates = self._duplicates(receipts)
        meal_totals = self._meal_totals(receipts, duplicates, trip)
        assessments = []

        for receipt in receipts:
            if receipt.receipt_id in duplicates:
                assessment = Assessment(
                    receipt=receipt,
                    decision=Decision.DUPLICATE,
                    reasons=(
                        "duplicate_of:" + duplicates[receipt.receipt_id],
                    ),
                )
            else:
                reasons = self._review_reasons(receipt, trip, meal_totals)
                decision = Decision.REVIEW if reasons else Decision.ELIGIBLE
                assessment = Assessment(
                    receipt=receipt,
                    decision=decision,
                    reasons=tuple(reasons),
                )
            assessments.append(assessment)

        return Evaluation(
            trip=trip,
            policy_version=self.version,
            assessments=tuple(assessments),
        )

    @staticmethod
    def _duplicates(receipts: Sequence[Receipt]) -> dict[str, str]:
        seen: dict[tuple[str, str, str], str] = {}
        duplicates: dict[str, str] = {}
        for receipt in receipts:
            identity = receipt.invoice_identity()
            if identity is None:
                continue

            if identity in seen:
                duplicates[receipt.receipt_id] = seen[identity]
            else:
                seen[identity] = receipt.receipt_id

        return duplicates

    @staticmethod
    def _meal_totals(
        receipts: Sequence[Receipt],
        duplicates: Mapping[str, str],
        trip: Trip,
    ) -> dict[date, Decimal]:
        totals: defaultdict[date, Decimal] = defaultdict(
            lambda: Decimal("0.00"),
        )
        for receipt in receipts:
            if (
                receipt.category == Category.MEAL
                and receipt.money.currency == "EUR"
                and trip.starts_on <= receipt.spent_on <= trip.ends_on
                and receipt.receipt_id not in duplicates
            ):
                totals[receipt.spent_on] += receipt.money.amount
        return dict(totals)

    def _review_reasons(
        self,
        receipt: Receipt,
        trip: Trip,
        meal_totals: Mapping[date, Decimal],
    ) -> list[str]:
        reasons = []
        if receipt.invoice_identity() is None:
            reasons.append("missing_invoice_number")
        if (
            not receipt.evidence_reference
            or not receipt.evidence_reference.strip()
        ):
            reasons.append("missing_evidence")
        if not trip.starts_on <= receipt.spent_on <= trip.ends_on:
            reasons.append("outside_trip_dates")

        if receipt.money.currency != "EUR":
            reasons.append("unsupported_currency")
            return reasons

        if (
            receipt.category == Category.HOTEL
            and receipt.money.amount > self.hotel_per_receipt
        ):
            reasons.append("hotel_receipt_limit_exceeded")
        if (
            receipt.category == Category.MEAL
            and meal_totals.get(receipt.spent_on, Decimal("0"))
            > self.meals_per_day
        ):
            reasons.append("daily_meal_limit_exceeded")

        return reasons
