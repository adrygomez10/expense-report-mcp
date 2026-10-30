"""Indicate a missing trip or one outside the employee's scope."""

from expense_report.domain.expense_error import ExpenseError


class TripUnavailableError(ExpenseError):
    """Indicate a missing trip or one outside the employee's scope."""
