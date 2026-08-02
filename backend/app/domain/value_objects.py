"""
Value objects: immutable, defined entirely by their attributes (no identity).

Two ComplexityEstimate objects with the same fields ARE the same value —
unlike entities (see entities.py), which have identity even if their
fields are identical.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import ComplexityClass, ConfidenceLevel


class CodeLocation(BaseModel):
    """Where in the source a finding applies. 1-indexed, inclusive."""

    model_config = ConfigDict(frozen=True)

    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)


class ComplexityEstimate(BaseModel):
    """
    A single complexity judgment (e.g. "worst-case time is O(n^2)") along
    with WHY the engine believes it and HOW confident it is. This triple
    (class, rationale, confidence) is mandatory on every estimate — a bare
    ComplexityClass with no rationale is exactly the kind of unexplained
    black-box answer STRIX exists to avoid.
    """

    model_config = ConfigDict(frozen=True)

    complexity_class: ComplexityClass
    rationale: str = Field(min_length=1, description="Human-readable reason for this estimate")
    confidence: ConfidenceLevel
