"""Indicate a missing draft or one outside the employee's scope."""

from expense_report.domain.expense_error import ExpenseError


class DraftUnavailableError(ExpenseError):
    """Indicate a missing draft or one outside the employee's scope."""
