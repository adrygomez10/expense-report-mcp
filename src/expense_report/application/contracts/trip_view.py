"""Describe one trip available to the configured employee."""

from typing import TypedDict


class TripView(TypedDict):
    """Describe one trip available to the configured employee."""

    trip_id: str
    destination: str
    starts_on: str
    ends_on: str
