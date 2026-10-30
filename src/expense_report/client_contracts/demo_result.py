"""Define the structured result of the programmed MCP demo."""

from typing import NotRequired, TypedDict

from pydantic import JsonValue

from expense_report.application.contracts.expense_draft import ExpenseDraft
from expense_report.application.contracts.report_snapshot import ReportSnapshot
from expense_report.client_contracts.demo_role import DemoRole


class DemoResult(TypedDict):
    """Keep the programmed demo output distinct from a model response."""

    role: DemoRole
    tools: list[str]
    policy: dict[str, JsonValue]
    prompt: dict[str, JsonValue]
    preview: ReportSnapshot
    draft: NotRequired[ExpenseDraft]
