"""Validate both collections as a single external document."""

from expense_report.adapters.travel.fixture_record import FixtureRecord
from expense_report.adapters.travel.receipt_record import ReceiptRecord
from expense_report.adapters.travel.trip_record import TripRecord


class TravelFixture(FixtureRecord):
    """Validate both collections as a single external document."""

    trips: tuple[TripRecord, ...]
    receipts: tuple[ReceiptRecord, ...]
