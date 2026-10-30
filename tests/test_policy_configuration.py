"""Verify policy versions and monetary limit validation."""

import unittest
from decimal import Decimal

from expense_report.domain.expense_error import ExpenseError
from expense_report.domain.expense_policy import ExpensePolicy


class PolicyConfigurationTests(unittest.TestCase):
    """Keep invalid configurable limits outside policy evaluation."""

    def test_invalid_limits_are_rejected(self) -> None:
        """Reject nonpositive, nonfinite and imprecise monetary limits."""
        for amount in ("0", "-1", "NaN", "Infinity", "1.001"):
            with self.subTest(amount=amount), self.assertRaises(ExpenseError):
                ExpensePolicy(meals_per_day=Decimal(amount))

    def test_policy_version_is_required(self) -> None:
        """Require a version so persisted decisions can be explained."""
        with self.assertRaises(ExpenseError):
            ExpensePolicy(version=" ")
