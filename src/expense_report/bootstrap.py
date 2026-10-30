"""Compose dependencies and start the local stdio transport explicitly."""

import argparse
from pathlib import Path

from expense_report.adapters.mcp.server import build_server
from expense_report.adapters.persistence.sqlite_draft_store import (
    SqliteDraftStore,
)
from expense_report.adapters.travel.json_travel_data import JsonTravelData
from expense_report.application.expense_service import ExpenseService
from expense_report.domain.expense_policy import ExpensePolicy


def main() -> None:
    """Bind a trusted demo identity and run the MCP process over stdio."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--employee", default="employee-01")
    parser.add_argument("--read-only", action="store_true")
    args = parser.parse_args()

    travel = JsonTravelData(args.fixtures)
    store = SqliteDraftStore(args.database)
    store.initialize()
    service = ExpenseService(
        travel=travel,
        drafts=store,
        policy=ExpensePolicy(),
        employee_id=args.employee,
    )
    server = build_server(service, read_only=args.read_only)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
