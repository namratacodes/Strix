"""
AnalyzeCodeUseCase: the central orchestration of STRIX's analysis pipeline.

This class is the direct code representation of the PRD's workflow:
  AST Parsing -> Static Analysis -> Algorithm Detection ->
  Complexity Engine -> LLM Explanation -> Merge Results -> Reasoning Timeline

It depends only on the abstract ports from application/ports.py — never on
concrete parsers, detectors, or LLM clients. This is what makes "pluggable
LLMs" and "AST + Tree-sitter" real architectural properties instead of just
PRD wishes: swapping OllamaExplainer for an OpenAI-backed one later means
writing one new adapter class, with ZERO changes to this file.
"""

from app.application.ports import (
    AlgorithmDetectorPort,
    ComplexityEstimatorPort,
    LanguageParserPort,
    LLMExplainerPort,
)
from app.domain.entities import AnalysisResult, CodeSubmission, ReasoningStep


class AnalyzeCodeUseCase:
    def __init__(
        self,
        parser: LanguageParserPort,
        algorithm_detector: AlgorithmDetectorPort,
        complexity_estimator: ComplexityEstimatorPort,
        explainer: LLMExplainerPort,
    ) -> None:
        self._parser = parser
        self._algorithm_detector = algorithm_detector
        self._complexity_estimator = complexity_estimator
        self._explainer = explainer

    def execute(self, submission: CodeSubmission) -> AnalysisResult:
        timeline: list[ReasoningStep] = []

        graph = self._parser.parse(submission.source_code)
        timeline.append(
            ReasoningStep(
                order=0,
                title="Building code graph",
                detail=f"Parsed {submission.language.value} source into an analysis graph.",
            )
        )

        algorithm_matches = self._algorithm_detector.detect(graph)
        timeline.append(
            ReasoningStep(
                order=1,
                title="Detecting algorithm patterns",
                detail=f"Found {len(algorithm_matches)} candidate pattern(s).",
            )
        )

        complexity = self._complexity_estimator.estimate(graph)
        timeline.append(
            ReasoningStep(
                order=2,
                title="Estimating complexity",
                detail=f"Worst case: {complexity.worst_case.complexity_class.value}.",
            )
        )

        explanation = self._explainer.explain(algorithm_matches, complexity)
        timeline.append(
            ReasoningStep(
                order=3,
                title="Generating explanation",
                detail="Converted findings into a beginner-friendly explanation.",
            )
        )

        return AnalysisResult(
            submission_id=submission.id,
            algorithm_matches=algorithm_matches,
            complexity=complexity,
            reasoning_timeline=timeline,
            explanation=explanation,
        )
