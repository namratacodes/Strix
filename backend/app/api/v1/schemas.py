"""
API-layer schemas. Kept separate from domain entities so the HTTP
contract can evolve independently of internal domain modeling -- e.g.
CodeSubmission auto-generates an id/timestamp that a request body should
never need to supply.

AnalysisResult (the response) is reused directly from the domain layer
for this milestone -- it's already a clean, framework-agnostic Pydantic
model with no leaked internals. A dedicated response DTO can be
introduced later if the API contract needs to diverge from the domain
model (e.g. API versioning); noted as a deliberate simplification, not
an oversight.
"""

from pydantic import BaseModel, Field

from app.domain.enums import Language


class AnalyzeRequest(BaseModel):
    source_code: str = Field(
        min_length=1,
        max_length=20_000,
        description="Source code to analyze.",
    )
    language: Language = Language.PYTHON