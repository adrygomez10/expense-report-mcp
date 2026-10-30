"""Enforce inward imports using Python's AST rather than Java tooling."""

import ast
import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "src" / "expense_report"


class ArchitectureTests(unittest.TestCase):
    """Make a framework dependency in the core fail the test suite."""

    def test_dependencies_point_inward(self):
        """Restrict domain and application imports to their allowed layers."""
        for layer, allowed in (
            ("domain", {"domain"}),
            ("application", {"domain", "application"}),
        ):
            for path in (SOURCE / layer).rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    modules = []
                    if isinstance(node, ast.Import):
                        modules = [name.name for name in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        self.assertEqual(0, node.level, str(path))
                        modules = [node.module or ""]
                    for module in modules:
                        if module.startswith("expense_report."):
                            self.assertIn(module.split(".")[1], allowed)
                        else:
                            self.assertIn(
                                module.split(".")[0],
                                sys.stdlib_module_names,
                            )

    def test_importing_entry_points_performs_no_io(self):
        """Reject file reads, connections and server startup on import."""
        with (
            patch(
                "pathlib.Path.read_text", side_effect=AssertionError("read")
            ),
            patch("sqlite3.connect", side_effect=AssertionError("connect")),
            patch(
                "mcp.server.MCPServer.run", side_effect=AssertionError("run")
            ),
        ):
            for name in ("expense_report.bootstrap", "expense_report.clients"):
                importlib.reload(importlib.import_module(name))
