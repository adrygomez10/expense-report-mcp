"""Run a reproducible MCP workflow without pretending to execute an LLM."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp.types import CallToolResult
from pydantic import TypeAdapter

from expense_report.application.contracts.expense_draft import ExpenseDraft
from expense_report.application.contracts.report_snapshot import ReportSnapshot
from expense_report.client_contracts.demo_result import DemoResult
from expense_report.client_contracts.demo_role import DemoRole


def parameters(
    fixtures: Path,
    database: Path,
    read_only: bool,
) -> StdioServerParameters:
    """Build an explicit subprocess command with absolute data paths."""
    args = [
        "-m",
        "expense_report.bootstrap",
        "--fixtures",
        str(fixtures.resolve()),
        "--database",
        str(database.resolve()),
    ]
    if read_only:
        args.append("--read-only")

    return StdioServerParameters(command=sys.executable, args=args)


async def demonstrate(
    fixtures: Path, database: Path, role: DemoRole, draft_id: str | None = None
) -> DemoResult:
    """Discover capabilities and perform a scripted employee/reviewer flow."""
    read_only = role == "reviewer"
    async with Client(parameters(fixtures, database, read_only)) as client:
        tools = await client.list_tools()
        policy = await client.read_resource("expense-policy://current")
        prompt = await client.get_prompt(
            "prepare_expense_report",
            {"trip_id": "trip-madrid"},
        )
        result = await client.call_tool(
            "preview_expense_report",
            {"trip_id": "trip-madrid"},
        )
        preview = TypeAdapter(ReportSnapshot).validate_python(
            _tool_data(result),
        )

        output: DemoResult = {
            "role": role,
            "tools": [tool.name for tool in tools.tools],
            "policy": policy.model_dump(mode="json"),
            "prompt": prompt.model_dump(mode="json"),
            "preview": preview,
        }

        if not read_only:
            draft = await client.call_tool(
                "create_expense_draft",
                {"trip_id": "trip-madrid"},
            )
            output["draft"] = TypeAdapter(ExpenseDraft).validate_python(
                _tool_data(draft),
            )

        if read_only and draft_id is not None:
            draft = await client.call_tool(
                "get_expense_draft",
                {"draft_id": draft_id},
            )
            output["draft"] = TypeAdapter(ExpenseDraft).validate_python(
                _tool_data(draft),
            )

        return output


def _tool_data(result: CallToolResult) -> object:
    """Reject tool failures and missing structured responses explicitly."""
    if result.is_error:
        raise RuntimeError(str(result.content))
    if result.structured_content is None:
        raise RuntimeError("The tool returned no structured content.")

    return result.structured_content


def main() -> None:
    """Print an actual protocol result; create no connections on import."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures", type=Path, default=Path("fixtures/travel.json")
    )
    parser.add_argument(
        "--database", type=Path, default=Path("data/expenses.db")
    )
    parser.add_argument(
        "--role", choices=("employee", "reviewer"), default="employee"
    )
    parser.add_argument("--draft-id")
    args = parser.parse_args()

    output = asyncio.run(
        demonstrate(args.fixtures, args.database, args.role, args.draft_id)
    )

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
