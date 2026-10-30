"""Persist draft snapshots atomically with scoped reads and bounded locks."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import TypeAdapter

from expense_report.application.contracts.expense_draft import ExpenseDraft
from expense_report.application.contracts.report_snapshot import ReportSnapshot
from expense_report.application.errors.draft_conflict_error import (
    DraftConflictError,
)
from expense_report.application.errors.draft_unavailable_error import (
    DraftUnavailableError,
)

REPORT_ADAPTER = TypeAdapter(ReportSnapshot)


class SqliteDraftStore:
    """Keep one immutable report draft for each employee and trip."""

    def __init__(self, database: Path) -> None:
        """Remember the path without opening or creating a database."""
        self._database = database

    def initialize(self) -> None:
        """Create storage explicitly before serving requests."""
        self._database.parent.mkdir(parents=True, exist_ok=True)

        with self._connection() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS drafts ("
                "draft_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL, "
                "trip_id TEXT NOT NULL, snapshot TEXT NOT NULL, "
                "created_at TEXT NOT NULL, UNIQUE(employee_id, trip_id))"
            )

    def save_once(
        self, employee_id: str, trip_id: str, snapshot: ReportSnapshot
    ) -> ExpenseDraft:
        """Serialize writers and reject replacing a different snapshot."""
        encoded = json.dumps(snapshot, sort_keys=True, ensure_ascii=False)

        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT draft_id, snapshot, created_at FROM drafts "
                "WHERE employee_id = ? AND trip_id = ?",
                (employee_id, trip_id),
            ).fetchone()

            if row is not None:
                if row[1] != encoded:
                    raise DraftConflictError(
                        "An earlier draft has different data; review it first."
                    )
                return self._view(row)

            row = (str(uuid4()), encoded, datetime.now(UTC).isoformat())
            connection.execute(
                "INSERT INTO drafts VALUES (?, ?, ?, ?, ?)",
                (row[0], employee_id, trip_id, row[1], row[2]),
            )
            return self._view(row)

    def get(self, employee_id: str, draft_id: str) -> ExpenseDraft:
        """Read only the selected employee's immutable draft."""
        with self._connection() as connection:
            row = connection.execute(
                "SELECT draft_id, snapshot, created_at FROM drafts "
                "WHERE employee_id = ? AND draft_id = ?",
                (employee_id, draft_id),
            ).fetchone()

        if row is None:
            raise DraftUnavailableError("Draft not found or unavailable.")

        return self._view(row)

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database, timeout=10)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    @staticmethod
    def _view(row: tuple[str, str, str]) -> ExpenseDraft:
        draft_id, snapshot, created_at = row

        return {
            "draft_id": draft_id,
            "status": "draft",
            "created_at": created_at,
            "report": REPORT_ADAPTER.validate_json(snapshot),
        }
