"""Represent the employee and inclusive dates of a business trip."""

from dataclasses import dataclass
from datetime import date

from expense_report.domain.expense_error import ExpenseError


@dataclass(frozen=True)
class Trip:
    """Represent the employee and inclusive dates of a business trip."""

    trip_id: str
    employee_id: str
    destination: str
    starts_on: date
    ends_on: date

    def __post_init__(self) -> None:
        """Ensure ownership and a nonempty, ordered trip period."""
        if not all(
            (
                self.trip_id.strip(),
                self.employee_id.strip(),
                self.destination.strip(),
            )
        ):
            raise ExpenseError(
                "Trip identifiers and destination are required."
            )

        if self.starts_on > self.ends_on:
            raise ExpenseError("Trip end must not precede its start.")
