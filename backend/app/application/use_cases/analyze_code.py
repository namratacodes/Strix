"""
AnalyzeCodeUseCase: the central orchestration of STRIX's analysis pipeline.

This class is the direct code representation of the PRD's workflow:
  AST Parsing -> Static Analysis -> Algorithm Detection ->
  Complexity Engine -> LLM Explanation -> Merge Results -> Reasoning Timeline

It depends only on the abstract ports from application/ports.py — never on
concrete parsers, detectors, or LLM clients. Timeline narration is
delegated to ReasoningTimelineBuilder (Milestone 6), keeping this class
focused purely on orchestration order, not narration detail.
"""

from app.application.ports import (
    AlgorithmDetectorPort,
    ComplexityEstimatorPort,
    LanguageParserPort,
    LLMExplainerPort,
)
from app.application.reasoning_timeline import ReasoningTimelineBuilder
from app.domain.entities import AnalysisResult, CodeSubmission


class AnalyzeCodeUseCase:
    def __init__(
        self,
        parser: LanguageParserPort,
        algorithm_detector: AlgorithmDetectorPort,
        complexity_estimator: ComplexityEstimatorPort,
        explainer: LLMExplainerPort,
        timeline_builder: ReasoningTimelineBuilder | None = None,
    ) -> None:
        self._parser = parser
        self._algorithm_detector = algorithm_detector
        self._complexity_estimator = complexity_estimator
        self._explainer = explainer
        self._timeline_builder = timeline_builder or ReasoningTimelineBuilder()

    def execute(self, submission: CodeSubmission) -> AnalysisResult:
        graph = self._parser.parse(submission.source_code)
        algorithm_matches = self._algorithm_detector.detect(graph)
        complexity = self._complexity_estimator.estimate(graph)
        explanation = self._explainer.explain(algorithm_matches, complexity)

        reasoning_timeline = self._timeline_builder.build(graph, algorithm_matches, complexity)

        return AnalysisResult(
            submission_id=submission.id,
            algorithm_matches=algorithm_matches,
            complexity=complexity,
            reasoning_timeline=reasoning_timeline,
            explanation=explanation,
        )