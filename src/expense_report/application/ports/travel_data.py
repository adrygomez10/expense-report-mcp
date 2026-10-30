"""Read trips and normalized receipts within an employee scope."""

from typing import Protocol

from expense_report.domain.receipt import Receipt
from expense_report.domain.trip import Trip


class TravelData(Protocol):
    """Read trips and normalized receipts within an employee scope."""

    def list_trips(self, employee_id: str) -> tuple[Trip, ...]:
        """Return only the selected employee's trips."""
        ...

    def get_trip(self, employee_id: str, trip_id: str) -> Trip:
        """Return an owned trip or raise an indistinguishable access error."""
        ...

    def receipts_for(self, trip_id: str) -> tuple[Receipt, ...]:
        """Return receipts after the use case has established trip access."""
        ...
