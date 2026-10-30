"""Distinguish eligible expenses from review and duplicate exclusion."""

from enum import StrEnum


class Decision(StrEnum):
    """Distinguish eligible expenses from review and duplicate exclusion."""

    ELIGIBLE = "eligible"
    REVIEW = "review"
    DUPLICATE = "duplicate"
