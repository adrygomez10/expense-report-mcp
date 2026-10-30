"""Preserve a receipt's provenance and policy decision."""

from typing import TypedDict

from expense_report.domain.category import Category
from expense_report.domain.decision import Decision


class AssessmentView(TypedDict):
    """Preserve a receipt's provenance and policy decision."""

    receipt_id: str
    vendor: str
    invoice_number: str | None
    spent_on: str
    category: Category
    amount: str
    currency: str
    evidence_reference: str | None
    decision: Decision
    reasons: list[str]
