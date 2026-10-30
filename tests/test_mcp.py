"""Exercise discovery, resources, prompts, errors and actual stdio calls."""

import tempfile
import unittest
from pathlib import Path

from mcp import Client

from expense_report.adapters.mcp.server import build_server
from expense_report.clients import parameters
from tests.support import FIXTURES, service_at


class McpTests(unittest.IsolatedAsyncioTestCase):
    """Run the SDK client against both in-process and subprocess servers."""

    def setUp(self):
        """Build isolated storage and a real protocol adapter."""
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.service = service_at(self.path)
        self.server = build_server(self.service, read_only=False)

    async def test_discovery_exposes_input_contract(self):
        """Advertise trip input and keep employee identity out of arguments."""
        async with Client(self.server, raise_exceptions=True) as client:
            tools = (await client.list_tools()).tools
        preview = next(
            tool for tool in tools if tool.name == "preview_expense_report"
        )
        self.assertEqual(["trip_id"], preview.input_schema["required"])
        self.assertNotIn("employee_id", preview.input_schema["properties"])
        self.assertTrue(preview.annotations.read_only_hint)

    async def test_read_only_profile_omits_and_rejects_write_tool(self):
        """Enforce capability restrictions on the server, not in prose."""
        server = build_server(self.service, read_only=True)
        async with Client(server, raise_exceptions=True) as client:
            tools = (await client.list_tools()).tools
            result = await client.call_tool(
                "create_expense_draft", {"trip_id": "trip-madrid"}
            )
        self.assertNotIn("create_expense_draft", [tool.name for tool in tools])
        self.assertTrue(result.is_error)

    async def test_policy_resource_and_prompt_are_available(self):
        """Read actual rules and render instructions without an LLM call."""
        async with Client(self.server, raise_exceptions=True) as client:
            policy = await client.read_resource("expense-policy://current")
            prompt = await client.get_prompt(
                "prepare_expense_report", {"trip_id": "trip-madrid"}
            )
        self.assertIn("35.00", str(policy))
        self.assertIn("trip-madrid", str(prompt))

    async def test_business_errors_are_explicit_tool_results(self):
        """Return an error result for a trip outside the employee scope."""
        async with Client(self.server, raise_exceptions=True) as client:
            result = await client.call_tool(
                "preview_expense_report", {"trip_id": "trip-private"}
            )
        self.assertTrue(result.is_error)
        self.assertIn("unavailable", str(result.content))

    async def test_stdio_round_trip_and_restart(self):
        """Persist a draft over stdio and read it from a new reader process."""
        database = self.path / "stdio.db"
        async with Client(parameters(FIXTURES, database, False)) as client:
            preview = await client.call_tool(
                "preview_expense_report", {"trip_id": "trip-madrid"}
            )
            draft = await client.call_tool(
                "create_expense_draft", {"trip_id": "trip-madrid"}
            )
        self.assertFalse(preview.is_error)
        self.assertEqual("249.90", preview.structured_content["eligible_eur"])
        self.assertFalse(draft.is_error)
        identifier = draft.structured_content["draft_id"]
        async with Client(parameters(FIXTURES, database, True)) as client:
            reread = await client.call_tool(
                "get_expense_draft", {"draft_id": identifier}
            )
        self.assertFalse(reread.is_error)
        self.assertEqual(draft.structured_content, reread.structured_content)
