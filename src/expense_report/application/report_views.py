"""Project domain values into explicit application response contracts."""

from expense_report.application.contracts.assessment_view import AssessmentView
from expense_report.application.contracts.report_snapshot import ReportSnapshot
from expense_report.application.contracts.trip_view import TripView
from expense_report.domain.assessment import Assessment
from expense_report.domain.decision import Decision
from expense_report.domain.evaluation import Evaluation
from expense_report.domain.trip import Trip


def evaluation_view(evaluation: Evaluation) -> ReportSnapshot:
    """Build an explicit serializable report without approving payments."""
    return {
        "trip_id": evaluation.trip.trip_id,
        "policy_version": evaluation.policy_version,
        "currency": "EUR",
        "total_eur": format(evaluation.total(), ".2f"),
        "eligible_eur": format(evaluation.total(Decision.ELIGIBLE), ".2f"),
        "review_eur": format(evaluation.total(Decision.REVIEW), ".2f"),
        "excluded_duplicate_eur": format(
            evaluation.total(Decision.DUPLICATE),
            ".2f",
        ),
        "lines": [_assessment_view(item) for item in evaluation.assessments],
    }


def _assessment_view(assessment: Assessment) -> AssessmentView:
    """Project one receipt and its decision into the application response."""
    receipt = assessment.receipt

    return {
        "receipt_id": receipt.receipt_id,
        "vendor": receipt.vendor,
        "invoice_number": receipt.invoice_number,
        "spent_on": receipt.spent_on.isoformat(),
        "category": receipt.category,
        "amount": format(receipt.money.amount, ".2f"),
        "currency": receipt.money.currency,
        "evidence_reference": receipt.evidence_reference,
        "decision": assessment.decision,
        "reasons": list(assessment.reasons),
    }


def trip_view(trip: Trip) -> TripView:
    """Project one owned trip into the application response."""
    return {
        "trip_id": trip.trip_id,
        "destination": trip.destination,
        "starts_on": trip.starts_on.isoformat(),
        "ends_on": trip.ends_on.isoformat(),
    }
