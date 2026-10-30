"""Return a policy-versioned report with decimal amounts as strings."""

from expense_report.adapters.mcp.line_output import LineOutput
from expense_report.adapters.mcp.transport_output import TransportOutput


class ReportOutput(TransportOutput):
    """Return a policy-versioned report with decimal amounts as strings."""

    trip_id: str
    policy_version: str
    currency: str
    total_eur: str
    eligible_eur: str
    review_eur: str
    excluded_duplicate_eur: str
    lines: list[LineOutput]
