"""Parse a trip with explicit ownership and ISO travel dates."""

from datetime import date

from expense_report.adapters.travel.fixture_record import FixtureRecord


class TripRecord(FixtureRecord):
    """Parse a trip with explicit ownership and ISO travel dates."""

    trip_id: str
    employee_id: str
    destination: str
    starts_on: date
    ends_on: date
