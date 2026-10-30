"""Expose receipt provenance and its policy assessment."""

from datetime import date

from expense_report.adapters.mcp.transport_output import TransportOutput
from expense_report.domain.category import Category
from expense_report.domain.decision import Decision


class LineOutput(TransportOutput):
    """Expose receipt provenance and its policy assessment."""

    receipt_id: str
    vendor: str
    invoice_number: str | None
    spent_on: date
    category: Category
    amount: str
    currency: str
    evidence_reference: str | None
    decision: Decision
    reasons: list[str]
