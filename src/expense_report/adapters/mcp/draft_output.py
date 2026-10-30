"""Return the persisted identity, creation time and report snapshot."""

from typing import Literal

from pydantic import AwareDatetime

from expense_report.adapters.mcp.report_output import ReportOutput
from expense_report.adapters.mcp.transport_output import TransportOutput


class DraftOutput(TransportOutput):
    """Return the persisted identity, creation time and report snapshot."""

    draft_id: str
    status: Literal["draft"]
    created_at: AwareDatetime
    report: ReportOutput
