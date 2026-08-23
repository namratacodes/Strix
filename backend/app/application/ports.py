"""
Application ports: abstract contracts between the application layer and
infrastructure. This file defines WHAT the system needs, never HOW.

Concrete implementations (PythonASTParser, OllamaExplainer, etc.) live in
app/infrastructure/, and are wired in via constructor injection — the use
case in use_cases/ never imports them directly.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import AlgorithmMatch, AnalysisHistoryEntry, ComplexityResult, User

from app.application.dto import CodeGraph  # re-exported for existing imports
from app.domain.entities import AlgorithmMatch, ComplexityResult
from app.domain.enums import Language

__all__ = [
    "CodeGraph",
    "LanguageParserPort",
    "AlgorithmDetectorPort",
    "ComplexityEstimatorPort",
    "LLMExplainerPort",
    "UserRepositoryPort",
    "AnalysisHistoryRepositoryPort"
]


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
    Cannot assert complexity or algorithm identity — narrator-only role.
    """

    @abstractmethod
    def explain(
        self,
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult | None,
    ) -> str: ...
    
class UserRepositoryPort(ABC):
    """Persists and retrieves users, keyed by their Google account id."""

    @abstractmethod
    def get_or_create_by_google_id(
        self, google_id: str, email: str, display_name: str
    ) -> User: ...

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None: ...


class AnalysisHistoryRepositoryPort(ABC):
    """Persists and retrieves a user's past analyses."""

    @abstractmethod
    def save(self, entry: AnalysisHistoryEntry) -> AnalysisHistoryEntry: ...

    @abstractmethod
    def list_for_user(self, user_id: UUID, limit: int = 20) -> list[AnalysisHistoryEntry]: ...