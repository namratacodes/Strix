"""
Tests AnalyzeCodeUseCase using FAKE adapters (not real parsers/LLMs, which
don't exist until later milestones). This is the whole point of coding to
ports: we can prove the orchestration logic works correctly right now,
independent of any concrete implementation. When Milestone 3's real
PythonASTParser lands, this use case class won't need a single line
changed — only production wiring (main.py's dependency injection) will
point at the real adapter instead of a fake one.
"""

from app.application.ports import (
    AlgorithmDetectorPort,
    CodeGraph,
    ComplexityEstimatorPort,
    LanguageParserPort,
    LLMExplainerPort,
)
from app.application.use_cases.analyze_code import AnalyzeCodeUseCase
from app.domain.entities import AlgorithmMatch, CodeSubmission, ComplexityResult
from app.domain.enums import ConfidenceLevel, Language
from app.domain.value_objects import ComplexityEstimate


class FakeParser(LanguageParserPort):
    @property
    def supported_language(self) -> Language:
        return Language.PYTHON

    def parse(self, source_code: str) -> CodeGraph:
        return CodeGraph(language=Language.PYTHON, raw=source_code)


class FakeAlgorithmDetector(AlgorithmDetectorPort):
    def detect(self, graph: CodeGraph) -> list[AlgorithmMatch]:
        return [
            AlgorithmMatch(
                name="Bubble Sort",
                confidence=ConfidenceLevel.HIGH,
                rationale="Two nested loops with adjacent-element swaps.",
            )
        ]


class FakeComplexityEstimator(ComplexityEstimatorPort):
    def estimate(self, graph: CodeGraph) -> ComplexityResult:
        estimate = ComplexityEstimate(
            complexity_class="O(n^2)",  # validated against ComplexityClass enum
            rationale="Two nested loops over n.",
            confidence=ConfidenceLevel.HIGH,
        )
        return ComplexityResult(
            best_case=estimate, average_case=estimate, worst_case=estimate, space=estimate
        )


class FakeExplainer(LLMExplainerPort):
    def explain(self, algorithm_matches, complexity) -> str:
        return "This code sorts a list using Bubble Sort, which is O(n^2)."


def test_analyze_code_use_case_orchestrates_full_pipeline():
    use_case = AnalyzeCodeUseCase(
        parser=FakeParser(),
        algorithm_detector=FakeAlgorithmDetector(),
        complexity_estimator=FakeComplexityEstimator(),
        explainer=FakeExplainer(),
    )
    submission = CodeSubmission(source_code="def bubble_sort(arr): ...", language=Language.PYTHON)

    result = use_case.execute(submission)

    assert result.submission_id == submission.id
    assert len(result.algorithm_matches) == 1
    assert result.algorithm_matches[0].name == "Bubble Sort"
    assert result.complexity is not None
    assert result.complexity.worst_case.complexity_class.value == "O(n^2)"
    assert result.explanation is not None
    # Reasoning timeline must reflect every pipeline stage, in order
    assert [step.order for step in result.reasoning_timeline] == [0, 1, 2, 3]
