"""Coordinate expense preparation through the application ports."""

from expense_report.application.contracts.expense_draft import ExpenseDraft
from expense_report.application.contracts.policy_view import PolicyView
from expense_report.application.contracts.report_snapshot import ReportSnapshot
from expense_report.application.contracts.trip_collection import TripCollection
from expense_report.application.ports.draft_store import DraftStore
from expense_report.application.ports.travel_data import TravelData
from expense_report.application.report_views import evaluation_view, trip_view
from expense_report.domain.expense_policy import ExpensePolicy


class ExpenseService:
    """Prepare reports for the identity bound by the composition root."""

    def __init__(
        self,
        travel: TravelData,
        drafts: DraftStore,
        policy: ExpensePolicy,
        employee_id: str,
    ) -> None:
        """Receive ports, policy and a trusted local employee identity."""
        self._travel = travel
        self._drafts = drafts
        self._policy = policy
        self._employee_id = employee_id

    def list_trips(self) -> TripCollection:
        """List the employee's trip identifiers and travel dates."""
        trips = self._travel.list_trips(self._employee_id)

        return {"trips": [trip_view(trip) for trip in trips]}

    def preview(self, trip_id: str) -> ReportSnapshot:
        """Evaluate an owned trip without storing or submitting anything."""
        trip = self._travel.get_trip(self._employee_id, trip_id)
        receipts = self._travel.receipts_for(trip.trip_id)

        evaluation = self._policy.evaluate(trip, receipts)

        return evaluation_view(evaluation)

    def create_draft(self, trip_id: str) -> ExpenseDraft:
        """Persist a report once; retries cannot create duplicate drafts."""
        snapshot = self.preview(trip_id)

        return self._drafts.save_once(self._employee_id, trip_id, snapshot)

    def get_draft(self, draft_id: str) -> ExpenseDraft:
        """Read a draft within the bound employee identity."""
        return self._drafts.get(self._employee_id, draft_id)

    def policy_view(self) -> PolicyView:
        """Explain the same policy values used by the domain evaluation."""
        return {
            "version": self._policy.version,
            "currency": "EUR",
            "hotel_per_receipt_eur": str(self._policy.hotel_per_receipt),
            "meals_per_day_eur": str(self._policy.meals_per_day),
            "transport_limit": None,
            "dates": "inclusive trip dates",
            "evidence": "invoice number and evidence reference required",
            "duplicates": "vendor, invoice number and currency",
            "status": "fictional demo policy; eligibility is not approval",
        }
