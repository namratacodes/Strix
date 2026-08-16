"""
Data Transfer Objects: structures that move data between application-layer
components (parser -> algorithm detector -> complexity estimator) without
being core business entities in their own right.

CodeGraph lives here rather than in domain/ because it's an internal
analysis artifact, not a concept STRIX's business rules reason about
directly (unlike AnalysisResult, which IS a core domain entity).
"""

from dataclasses import dataclass, field
from typing import Any

from app.domain.enums import Language
from app.domain.value_objects import CodeLocation


@dataclass(frozen=True)
class LoopInfo:
    """One loop found in the source, with its nesting depth (1 = outermost)."""

    location: CodeLocation
    loop_type: str  # "for" | "while"
    nesting_depth: int


@dataclass(frozen=True)
class FunctionInfo:
    """Everything the static engine learned about a single top-level function."""

    name: str
    location: CodeLocation
    is_recursive: bool
    loops: tuple[LoopInfo, ...]
    max_nesting_depth: int
    calls: tuple[str, ...]
    
    raw_node: Any = field(default=None, repr=False, compare=False)


@dataclass
class CodeGraph:
    """
    Structured, language-agnostic representation of parsed source code.
    Produced by any LanguageParserPort implementation; consumed by
    AlgorithmDetectorPort and ComplexityEstimatorPort implementations.
    """

    language: Language
    functions: tuple[FunctionInfo, ...]
    top_level_loops: tuple[LoopInfo, ...]
    
    raw_tree: Any = field(default=None, repr=False, compare=False)