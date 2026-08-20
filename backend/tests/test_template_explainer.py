from app.domain.entities import AlgorithmMatch, ComplexityResult
from app.domain.enums import ConfidenceLevel
from app.domain.value_objects import ComplexityEstimate
from app.infrastructure.llm.template_explainer import TemplateExplainer

explainer = TemplateExplainer()


def _estimate(cls="O(n)"):
    return ComplexityEstimate(complexity_class=cls, rationale="x", confidence=ConfidenceLevel.HIGH)


def test_explains_with_matched_algorithm():
    match = AlgorithmMatch(name="Bubble Sort", confidence=ConfidenceLevel.HIGH, rationale="x")
    complexity = ComplexityResult(
        best_case=_estimate("O(n^2)"),
        average_case=_estimate("O(n^2)"),
        worst_case=_estimate("O(n^2)"),
        space=_estimate("O(1)"),
    )
    text = explainer.explain([match], complexity)
    assert "Bubble Sort" in text
    assert "O(n^2)" in text
    assert "O(1)" in text


def test_explains_with_no_algorithm_matched():
    complexity = ComplexityResult(
        best_case=_estimate(), average_case=_estimate(), worst_case=_estimate(), space=_estimate("O(1)")
    )
    text = explainer.explain([], complexity)
    assert "No specific algorithm pattern" in text


def test_handles_missing_complexity_gracefully():
    text = explainer.explain([], None)
    assert "No specific algorithm pattern" in text