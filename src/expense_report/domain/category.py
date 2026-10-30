"""Classify the supported expense categories."""

from enum import StrEnum


class Category(StrEnum):
    """Classify the supported expense categories."""

    TRANSPORT = "transport"
    HOTEL = "hotel"
    MEAL = "meal"
