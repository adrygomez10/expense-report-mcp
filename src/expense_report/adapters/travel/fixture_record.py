"""Reject unknown fields and coercion in externally supplied records."""

from pydantic import BaseModel, ConfigDict


class FixtureRecord(BaseModel):
    """Reject unknown fields and coercion in externally supplied records."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
