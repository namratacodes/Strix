"""
TemplateExplainer: a deterministic, LLM-free implementation of
LLMExplainerPort. Composes a beginner-friendly summary directly from the
analysis facts using fixed templates -- no network call, no model required.

Purpose:
- Safe default while developing (zero setup).
- A genuine second implementation of the port, proving LLMExplainerPort
  is actually swappable rather than a single-implementation abstraction.
- Usable as a fallback if Ollama is unreachable.
"""

from app.application.ports import LLMExplainerPort
from app.domain.entities import AlgorithmMatch, ComplexityResult


class TemplateExplainer(LLMExplainerPort):
    def explain(
        self,
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult | None,
    ) -> str:
        parts: list[str] = []

        if algorithm_matches:
            names = ", ".join(match.name for match in algorithm_matches)
            parts.append(f"This code appears to implement {names}.")
        else:
            parts.append(
                "No specific algorithm pattern was confidently matched for this code."
            )

        if complexity:
            parts.append(
                f"Its worst-case time complexity is {complexity.worst_case.complexity_class.value} "
                f"({complexity.worst_case.confidence.value} confidence): {complexity.worst_case.rationale}"
            )
            parts.append(
                f"It uses {complexity.space.complexity_class.value} auxiliary space "
                f"({complexity.space.confidence.value} confidence): {complexity.space.rationale}"
            )

        return " ".join(parts)