"""Reject undeclared fields at the outgoing protocol boundary."""

from pydantic import BaseModel, ConfigDict


class TransportOutput(BaseModel):
    """Reject undeclared fields at the outgoing protocol boundary."""

    model_config = ConfigDict(extra="forbid")
