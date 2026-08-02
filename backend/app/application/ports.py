"""
Application ports: abstract contracts between the application layer and
infrastructure. This file defines WHAT the system needs, never HOW.

Concrete implementations (PythonASTParser, OllamaExplainer, etc.) live in
app/infrastructure/ starting in Milestone 3, and are wired in via
constructor injection — the use case below never imports them directly.

`CodeGraph` is a deliberately minimal placeholder for now. Milestone 3
will flesh it out into the real intermediate representation (nodes for
loops, function calls, recursion, etc.) that both the Python AST parser
and the Tree-sitter parser produce, so downstream engines (algorithm
detection, complexity estimation) don't care which parser built it.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities import AlgorithmMatch, ComplexityResult
from app.domain.enums import Language


class CodeGraph:
    """
    Placeholder intermediate representation of parsed code.
    Replaced with a real structured graph in Milestone 3.
    """

    def __init__(self, language: Language, raw: Any = None) -> None:
        self.language = language
        self.raw = raw


class LanguageParserPort(ABC):
    """Parses raw source code into a language-agnostic CodeGraph."""

    @abstractmethod
    def parse(self, source_code: str) -> CodeGraph: ...

    @property
    @abstractmethod
    def supported_language(self) -> Language: ...


class AlgorithmDetectorPort(ABC):
    """Identifies known algorithm patterns within a CodeGraph."""

    @abstractmethod
    def detect(self, graph: CodeGraph) -> list[AlgorithmMatch]: ...


class ComplexityEstimatorPort(ABC):
    """Estimates time/space complexity from a CodeGraph."""

    @abstractmethod
    def estimate(self, graph: CodeGraph) -> ComplexityResult: ...


class LLMExplainerPort(ABC):
    """
    Turns deterministic findings into natural-language explanation.

    Deliberately narrow: this port can ONLY produce text. It has no method
    that lets it assert a complexity class or algorithm name — that
    guarantees the LLM narrates the static engine's conclusions, it can
    never originate or override them (Core Philosophy #1: never blindly
    trust the LLM).
    """

    @abstractmethod
    def explain(
        self,
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult | None,
    ) -> str: ...
