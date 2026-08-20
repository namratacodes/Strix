"""
ResilientExplainer: wraps a primary LLMExplainerPort with a fallback.

This is what makes STRIX's LLM layer production-safe rather than a demo
that breaks the moment Ollama isn't running: if the primary explainer
raises anything at all, we log it and fall back to a deterministic
explanation instead of failing the whole analysis. The rest of the
analysis (algorithm detection, complexity, reasoning timeline) is
unaffected either way, since none of it depends on the LLM.
"""

import logging

from app.application.ports import LLMExplainerPort
from app.domain.entities import AlgorithmMatch, ComplexityResult

logger = logging.getLogger(__name__)


class ResilientExplainer(LLMExplainerPort):
    def __init__(self, primary: LLMExplainerPort, fallback: LLMExplainerPort) -> None:
        self._primary = primary
        self._fallback = fallback

    def explain(
        self,
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult | None,
    ) -> str:
        try:
            return self._primary.explain(algorithm_matches, complexity)
        except Exception as exc:  # noqa: BLE001 -- any primary failure must fall back safely
            logger.warning(
                "Primary LLM explainer failed (%s); using deterministic fallback.", exc
            )
            return self._fallback.explain(algorithm_matches, complexity)