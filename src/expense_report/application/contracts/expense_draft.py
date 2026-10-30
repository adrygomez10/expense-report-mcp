"""Describe one persisted draft and its complete immutable snapshot."""

from typing import Literal, TypedDict

from expense_report.application.contracts.report_snapshot import ReportSnapshot


class ExpenseDraft(TypedDict):
    """Describe one persisted draft and its complete immutable snapshot."""

    draft_id: str
    status: Literal["draft"]
    created_at: str
    report: ReportSnapshot
