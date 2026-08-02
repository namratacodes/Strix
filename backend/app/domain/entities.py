"""
Entities: domain objects with identity that persists across changes.

Unlike value objects, two CodeSubmission instances with identical source
code are still two different submissions (different ids, different
timestamps) — identity, not attribute-equality, is what defines them.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.domain.enums import ConfidenceLevel, Language
from app.domain.value_objects import CodeLocation, ComplexityEstimate


class CodeSubmission(BaseModel):
    """A single piece of code submitted for analysis."""

    id: UUID = Field(default_factory=uuid4)
    source_code: str = Field(min_length=1)
    language: Language
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlgorithmMatch(BaseModel):
    """
    A detected algorithm pattern (e.g. "Binary Search" found at lines 4-12).

    `confidence` matters here for the same reason as ComplexityEstimate:
    pattern matching on an AST is a heuristic. A textbook binary search is
    HIGH confidence; something that merely resembles one is MEDIUM/LOW.
    """

    name: str = Field(min_length=1)
    confidence: ConfidenceLevel
    location: CodeLocation | None = None
    rationale: str = Field(min_length=1)


class ReasoningStep(BaseModel):
    """
    One entry in the AI Reasoning Timeline — STRIX's signature feature.

    `order` is explicit (not inferred from list position) so the timeline
    can be safely reordered, filtered, or streamed incrementally to the
    frontend without losing its intended sequence.
    """

    order: int = Field(ge=0)
    title: str = Field(min_length=1, description='e.g. "Detecting nested loops"')
    detail: str = Field(min_length=1, description='e.g. "Found 2 nested loops over n"')


class ComplexityResult(BaseModel):
    """Aggregate time + space complexity findings for one submission."""

    best_case: ComplexityEstimate
    average_case: ComplexityEstimate
    worst_case: ComplexityEstimate
    space: ComplexityEstimate


class AnalysisResult(BaseModel):
    """
    The full output of analyzing one CodeSubmission: everything the
    frontend needs to render the Reasoning Timeline, complexity graph,
    and algorithm detection panel in one response.
    """

    submission_id: UUID
    algorithm_matches: list[AlgorithmMatch] = Field(default_factory=list)
    complexity: ComplexityResult | None = None
    reasoning_timeline: list[ReasoningStep] = Field(default_factory=list)
    explanation: str | None = Field(
        default=None, description="LLM-generated natural-language summary"
    )
