"""
Core domain enums.

These are pure Python — no framework imports — because the domain layer
must never depend on FastAPI, Pydantic being used for HTTP, or any
infrastructure detail. (We do use Pydantic's Enum-friendly BaseModel in
value_objects.py/entities.py purely for validation convenience, not because
the domain "needs" a web framework.)
"""

from enum import Enum


class Language(str, Enum):
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
    JAVASCRIPT = "javascript"


class ConfidenceLevel(str, Enum):
    """
    How sure the analysis engine is about a given result.

    This exists because static analysis is a heuristic, not a proof. A
    nested-loop count is HIGH confidence; a recursive pattern that *might*
    be O(2^n) depending on memoization is MEDIUM/LOW. Every complexity or
    algorithm result must carry one of these — it's not optional metadata,
    it's core to STRIX's "explain how, and how sure" identity.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComplexityClass(str, Enum):
    """
    Ordered Big-O complexity classes, matching the PRD's Complexity Graph.

    Stored as an enum (not a bare string) so invalid values are rejected at
    construction time, and ordered via `rank` so the graph/UI can position
    a detected result along the O(1) -> O(n!) axis without a separate
    lookup table.
    """

    O_1 = "O(1)"
    O_LOG_N = "O(log n)"
    O_N = "O(n)"
    O_N_LOG_N = "O(n log n)"
    O_N_SQUARED = "O(n^2)"
    O_2_N = "O(2^n)"
    O_N_FACTORIAL = "O(n!)"

    @property
    def rank(self) -> int:
        order = [
            ComplexityClass.O_1,
            ComplexityClass.O_LOG_N,
            ComplexityClass.O_N,
            ComplexityClass.O_N_LOG_N,
            ComplexityClass.O_N_SQUARED,
            ComplexityClass.O_2_N,
            ComplexityClass.O_N_FACTORIAL,
        ]
        return order.index(self)

    def __lt__(self, other: "ComplexityClass") -> bool:
        return self.rank < other.rank
