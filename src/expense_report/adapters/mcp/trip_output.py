"""Describe one visible employee trip."""

from datetime import date

from expense_report.adapters.mcp.transport_output import TransportOutput


class TripOutput(TransportOutput):
    """Describe one visible employee trip."""

    trip_id: str
    destination: str
    starts_on: date
    ends_on: date
