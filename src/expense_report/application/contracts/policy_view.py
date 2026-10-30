"""Expose the exact policy values used by report evaluation."""

from typing import Literal, TypedDict


class PolicyView(TypedDict):
    """Expose the exact policy values used by report evaluation."""

    version: str
    currency: Literal["EUR"]
    hotel_per_receipt_eur: str
    meals_per_day_eur: str
    transport_limit: None
    dates: str
    evidence: str
    duplicates: str
    status: str
