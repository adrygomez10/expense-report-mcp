"""Reject malformed travel records at the input boundary."""

import json
import tempfile
import unittest
from pathlib import Path

from expense_report.adapters.travel.json_travel_data import JsonTravelData
from expense_report.domain.expense_error import ExpenseError
from tests.support import FIXTURES


class FixtureBoundaryTests(unittest.TestCase):
    """Reject malformed external data before it reaches the domain."""

    def test_invalid_document_shapes_are_rejected(self) -> None:
        """Reject malformed JSON and unexpected top-level values."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "travel.json"
            for content in ("{", "[]", "null", '{"trips": []}'):
                with self.subTest(content=content):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaises(ExpenseError):
                        JsonTravelData(path)

    def test_invalid_receipt_fields_are_rejected(self) -> None:
        """Refuse coercion, invalid dates, categories and extra fields."""
        cases = (
            ("vendor", 42),
            ("spent_on", "not-a-date"),
            ("category", "unknown"),
            ("unexpected_field", "value"),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "travel.json"
            for field, value in cases:
                with self.subTest(field=field):
                    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
                    data["receipts"][0][field] = value
                    path.write_text(json.dumps(data), encoding="utf-8")
                    with self.assertRaises(ExpenseError):
                        JsonTravelData(path)
