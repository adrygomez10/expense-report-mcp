"""Build isolated application instances with temporary persistence."""

from pathlib import Path

from expense_report.adapters.persistence.sqlite_draft_store import (
    SqliteDraftStore,
)
from expense_report.adapters.travel.json_travel_data import JsonTravelData
from expense_report.application.expense_service import ExpenseService
from expense_report.domain.expense_policy import ExpensePolicy

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "travel.json"


def service_at(directory: Path, employee: str = "employee-01"):
    """Compose real fixture and SQLite adapters for the selected identity."""
    store = SqliteDraftStore(directory / "test.db")
    store.initialize()
    return ExpenseService(
        travel=JsonTravelData(FIXTURES),
        drafts=store,
        policy=ExpensePolicy(),
        employee_id=employee,
    )
