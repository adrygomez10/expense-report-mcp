"""Read explicitly supplied, normalized travel fixtures from JSON."""

from collections.abc import Iterable
from decimal import Decimal, InvalidOperation
from pathlib import Path

from pydantic import ValidationError

from expense_report.adapters.travel.receipt_record import ReceiptRecord
from expense_report.adapters.travel.travel_fixture import TravelFixture
from expense_report.adapters.travel.trip_record import TripRecord
from expense_report.application.errors.trip_unavailable_error import (
    TripUnavailableError,
)
from expense_report.domain.expense_error import ExpenseError
from expense_report.domain.money import Money
from expense_report.domain.receipt import Receipt
from expense_report.domain.trip import Trip


class JsonTravelData:
    """Keep immutable fixture records; never accept file paths from tools."""

    def __init__(self, path: Path) -> None:
        """Validate external fields before constructing domain objects."""
        try:
            fixture = TravelFixture.model_validate_json(
                path.read_text(encoding="utf-8"),
            )
            self._trips = self._read_trips(fixture.trips)
            self._receipts = self._read_receipts(fixture.receipts)
        except (ValidationError, InvalidOperation) as error:
            raise ExpenseError("Invalid travel fixture.") from error

        self._validate_trip_references()

    def list_trips(self, employee_id: str) -> tuple[Trip, ...]:
        """Filter trips by their persisted owner."""
        return tuple(
            trip for trip in self._trips if trip.employee_id == employee_id
        )

    def get_trip(self, employee_id: str, trip_id: str) -> Trip:
        """Use the same error for missing trips and other employees' trips."""
        for trip in self.list_trips(employee_id):
            if trip.trip_id == trip_id:
                return trip

        raise TripUnavailableError("Trip not found or unavailable.")

    def receipts_for(self, trip_id: str) -> tuple[Receipt, ...]:
        """Return normalized receipts in their stable source order."""
        return self._receipts.get(trip_id, ())

    @staticmethod
    def _read_trips(records: Iterable[TripRecord]) -> tuple[Trip, ...]:
        trips = []
        for record in records:
            trip = Trip(
                trip_id=record.trip_id,
                employee_id=record.employee_id,
                destination=record.destination,
                starts_on=record.starts_on,
                ends_on=record.ends_on,
            )
            trips.append(trip)

        return tuple(trips)

    @classmethod
    def _read_receipts(
        cls,
        records: Iterable[ReceiptRecord],
    ) -> dict[str, tuple[Receipt, ...]]:
        receipts_by_trip: dict[str, list[Receipt]] = {}
        for record in records:
            receipt = cls._receipt_from_record(record)
            receipts_by_trip.setdefault(record.trip_id, []).append(receipt)

        return {trip: tuple(items) for trip, items in receipts_by_trip.items()}

    @staticmethod
    def _receipt_from_record(record: ReceiptRecord) -> Receipt:
        money = Money(amount=Decimal(record.amount), currency=record.currency)

        return Receipt(
            receipt_id=record.receipt_id,
            vendor=record.vendor,
            invoice_number=record.invoice_number,
            spent_on=record.spent_on,
            category=record.category,
            money=money,
            evidence_reference=record.evidence_reference,
        )

    def _validate_trip_references(self) -> None:
        identifiers = [trip.trip_id for trip in self._trips]
        if len(set(identifiers)) != len(identifiers):
            raise ExpenseError("Trip identifiers must be unique.")

        if set(self._receipts) - set(identifiers):
            raise ExpenseError("Receipts must belong to an existing trip.")
