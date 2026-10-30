"""Return the visible trip collection."""

from expense_report.adapters.mcp.transport_output import TransportOutput
from expense_report.adapters.mcp.trip_output import TripOutput


class TripsOutput(TransportOutput):
    """Return the visible trip collection."""

    trips: list[TripOutput]
