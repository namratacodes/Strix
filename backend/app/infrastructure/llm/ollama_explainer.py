"""
OllamaExplainer: calls a local Ollama instance to narrate the static
engine's already-decided facts in natural language.

Enforcement of "narrator, not decider" (Core Philosophy #1) happens on
TWO independent layers:
  1. Structural: LLMExplainerPort.explain() can only return a str -- there
     is no method on this port that lets the LLM assert a complexity
     class or algorithm name. Even a fully "jailbroken" model response
     can only ever become explanation text, never a decision.
  2. Prompt-level: the prompt explicitly lists the facts as already
     decided and instructs the model not to contradict them.
"""

import httpx

from app.application.ports import LLMExplainerPort
from app.domain.entities import AlgorithmMatch, ComplexityResult


class OllamaExplainerError(Exception):
    """Raised when the LLM backend cannot be reached or returns nothing usable."""


class OllamaExplainer(LLMExplainerPort):
    def __init__(self, base_url: str, model: str, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds

    def explain(
        self,
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult | None,
    ) -> str:
        prompt = self._build_prompt(algorithm_matches, complexity)
        try:
            response = httpx.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaExplainerError(
                f"Could not reach Ollama at {self._base_url}: {exc}"
            ) from exc

        text = response.json().get("response", "").strip()
        if not text:
            raise OllamaExplainerError("Ollama returned an empty response.")
        return text

    def _build_prompt(
        self,
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult | None,
    ) -> str:
        facts = self._summarize_facts(algorithm_matches, complexity)
        return (
            "You are STRIX, an explainable code intelligence assistant. "
            "The facts below were already determined by deterministic static "
            "analysis. Your ONLY job is to explain them in clear, beginner-"
            "friendly language.\n\n"
            "STRICT RULES:\n"
            "- Do NOT invent, contradict, or second-guess any fact below.\n"
            "- Do NOT state a different algorithm name or complexity class "
            "than given.\n"
            "- Do NOT add confidence claims beyond what is given.\n"
            "- Keep the explanation to 2-4 short sentences.\n\n"
            f"FACTS:\n{facts}\n\n"
            "Explanation:"
        )

    @staticmethod
    def _summarize_facts(
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult | None,
    ) -> str:
        lines: list[str] = []
        if algorithm_matches:
            for match in algorithm_matches:
                lines.append(
                    f"- Detected algorithm: {match.name} "
                    f"({match.confidence.value} confidence) — {match.rationale}"
                )
        else:
            lines.append("- No algorithm pattern was confidently matched.")

        if complexity is not None:
            lines.append(
                f"- Worst-case time complexity: {complexity.worst_case.complexity_class.value} "
                f"({complexity.worst_case.confidence.value} confidence) — "
                f"{complexity.worst_case.rationale}"
            )
            lines.append(
                f"- Auxiliary space complexity: {complexity.space.complexity_class.value} "
                f"({complexity.space.confidence.value} confidence) — {complexity.space.rationale}"
            )
        return "\n".join(lines)