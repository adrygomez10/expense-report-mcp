"""Keep one receipt's decision and the reasons that explain it."""

from dataclasses import dataclass

from expense_report.domain.decision import Decision
from expense_report.domain.receipt import Receipt


@dataclass(frozen=True)
class Assessment:
    """Keep one receipt's decision and the reasons that explain it."""

    receipt: Receipt
    decision: Decision
    reasons: tuple[str, ...]
