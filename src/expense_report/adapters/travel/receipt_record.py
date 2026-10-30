"""Parse a receipt while requiring textual decimal amounts."""

from datetime import date

from expense_report.adapters.travel.fixture_record import FixtureRecord
from expense_report.domain.category import Category


class ReceiptRecord(FixtureRecord):
    """Parse a receipt while requiring textual decimal amounts."""

    trip_id: str
    receipt_id: str
    vendor: str
    invoice_number: str | None
    spent_on: date
    category: Category
    amount: str
    currency: str
    evidence_reference: str | None
