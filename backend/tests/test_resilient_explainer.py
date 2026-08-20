from app.application.ports import LLMExplainerPort
from app.domain.entities import ComplexityResult
from app.domain.enums import ConfidenceLevel
from app.domain.value_objects import ComplexityEstimate
from app.infrastructure.llm.resilient_explainer import ResilientExplainer


def _complexity():
    estimate = ComplexityEstimate(complexity_class="O(n)", rationale="x", confidence=ConfidenceLevel.HIGH)
    return ComplexityResult(best_case=estimate, average_case=estimate, worst_case=estimate, space=estimate)


class WorkingExplainer(LLMExplainerPort):
    def explain(self, algorithm_matches, complexity) -> str:
        return "primary succeeded"


class BrokenExplainer(LLMExplainerPort):
    def explain(self, algorithm_matches, complexity) -> str:
        raise RuntimeError("simulated LLM failure")


class FallbackExplainer(LLMExplainerPort):
    def explain(self, algorithm_matches, complexity) -> str:
        return "fallback used"


def test_uses_primary_when_it_succeeds():
    resilient = ResilientExplainer(primary=WorkingExplainer(), fallback=FallbackExplainer())
    result = resilient.explain([], _complexity())
    assert result == "primary succeeded"


def test_falls_back_when_primary_raises():
    resilient = ResilientExplainer(primary=BrokenExplainer(), fallback=FallbackExplainer())
    result = resilient.explain([], _complexity())
    assert result == "fallback used"