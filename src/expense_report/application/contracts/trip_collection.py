"""Return the employee's visible trips."""

from typing import TypedDict

from expense_report.application.contracts.trip_view import TripView


class TripCollection(TypedDict):
    """Return the employee's visible trips."""

    trips: list[TripView]
