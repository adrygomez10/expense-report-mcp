"""Verify scoped preparation and durable expense drafts."""

import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from expense_report.adapters.persistence.sqlite_draft_store import (
    SqliteDraftStore,
)
from expense_report.adapters.travel.json_travel_data import JsonTravelData
from expense_report.domain.expense_error import ExpenseError
from tests.support import FIXTURES, service_at


class ApplicationTests(unittest.TestCase):
    """Use isolated real adapters to verify application guarantees."""

    def setUp(self):
        """Create a temporary database for every scenario."""
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.service = service_at(self.path)

    def test_demo_totals_and_reasons(self):
        """Match the article's worked example with actual policy results."""
        report = self.service.preview("trip-madrid")
        self.assertEqual("353.90", report["total_eur"])
        self.assertEqual("249.90", report["eligible_eur"])
        self.assertEqual("82.00", report["review_eur"])
        self.assertEqual("22.00", report["excluded_duplicate_eur"])
        self.assertEqual(6, len(report["lines"]))

    def test_other_employee_trip_is_not_readable(self):
        """Give foreign and missing trip identifiers the same failure."""
        messages = []
        for identifier in ("trip-private", "unknown"):
            with self.assertRaises(ExpenseError) as error:
                self.service.preview(identifier)
            messages.append(str(error.exception))
        self.assertEqual(messages[0], messages[1])

    def test_trip_listing_is_scoped(self):
        """List only owned travel records."""
        self.assertEqual(
            ["trip-madrid"],
            [trip["trip_id"] for trip in self.service.list_trips()["trips"]],
        )

    def test_retries_return_same_draft(self):
        """Keep identifiers and creation time stable across repeated calls."""
        first = self.service.create_draft("trip-madrid")
        self.assertEqual(first, self.service.create_draft("trip-madrid"))
        self.assertEqual("draft", first["status"])

    def test_restart_preserves_draft(self):
        """Read persisted state after composing a second application."""
        first = self.service.create_draft("trip-madrid")
        second_service = service_at(self.path)
        self.assertEqual(first, second_service.get_draft(first["draft_id"]))

    def test_other_employee_cannot_read_draft(self):
        """Enforce owner scoping at the storage query as well."""
        draft = self.service.create_draft("trip-madrid")
        other = service_at(self.path, "employee-02")
        with self.assertRaises(ExpenseError):
            other.get_draft(draft["draft_id"])

    def test_concurrent_retries_create_one_draft(self):
        """Serialize competing writers with a database transaction."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self.service.create_draft, "trip-madrid")
                for _ in range(4)
            ]
            identifiers = {future.result()["draft_id"] for future in futures}
        self.assertEqual(1, len(identifiers))

    def test_changed_snapshot_does_not_replace_original(self):
        """Require an explicit future amendment workflow for changed data."""
        first = self.service.create_draft("trip-madrid")
        store = SqliteDraftStore(self.path / "test.db")
        changed = dict(first["report"], policy_version="different")
        with self.assertRaises(ExpenseError):
            store.save_once("employee-01", "trip-madrid", changed)
        self.assertEqual(first, self.service.get_draft(first["draft_id"]))

    def test_json_rejects_float_amounts(self):
        """Require textual decimal amounts in normalized fixture data."""
        data = json.loads(FIXTURES.read_text(encoding="utf-8"))
        data["receipts"][0]["amount"] = 89.9
        invalid = self.path / "invalid.json"
        invalid.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ExpenseError):
            JsonTravelData(invalid)

    def test_store_constructor_has_no_io(self):
        """Construct a persistence adapter without creating directories."""
        target = self.path / "absent" / "db.sqlite"
        SqliteDraftStore(target)
        self.assertFalse(target.parent.exists())
