"""Prevent silent replacement of an earlier report snapshot."""

from expense_report.domain.expense_error import ExpenseError


class DraftConflictError(ExpenseError):
    """Prevent silent replacement of an earlier report snapshot."""
