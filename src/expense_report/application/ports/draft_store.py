"""Persist immutable draft snapshots with one draft per employee trip."""

from typing import Protocol

from expense_report.application.contracts.expense_draft import ExpenseDraft
from expense_report.application.contracts.report_snapshot import ReportSnapshot


class DraftStore(Protocol):
    """Persist immutable draft snapshots with one draft per employee trip."""

    def save_once(
        self, employee_id: str, trip_id: str, snapshot: ReportSnapshot
    ) -> ExpenseDraft:
        """Create or return an identical draft; reject a changed snapshot."""
        ...

    def get(self, employee_id: str, draft_id: str) -> ExpenseDraft:
        """Read a draft only when it belongs to the selected employee."""
        ...
