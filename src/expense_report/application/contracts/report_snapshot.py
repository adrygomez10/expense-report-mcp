"""Partition EUR totals and retain all assessed receipt lines."""

from typing import Literal, TypedDict

from expense_report.application.contracts.assessment_view import AssessmentView


class ReportSnapshot(TypedDict):
    """Partition EUR totals and retain all assessed receipt lines."""

    trip_id: str
    policy_version: str
    currency: Literal["EUR"]
    total_eur: str
    eligible_eur: str
    review_eur: str
    excluded_duplicate_eur: str
    lines: list[AssessmentView]
