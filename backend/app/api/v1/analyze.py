"""
The /analyze endpoint: STRIX's core API surface.

This is the ONE file in the codebase allowed to import concrete
infrastructure classes (PythonASTParser, PythonAlgorithmDetector, etc.)
alongside the application-layer use case -- it's the composition root
where abstract ports get wired to real adapters via FastAPI's dependency
injection. Every other file depends only on ports.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.schemas import AnalyzeRequest
from app.application.use_cases.analyze_code import AnalyzeCodeUseCase
from app.core.config import Settings, get_settings
from app.domain.entities import AnalysisResult, CodeSubmission
from app.domain.enums import Language
from app.infrastructure.complexity.python_complexity_estimator import (
    PythonComplexityEstimator,
)
from app.infrastructure.detection.python_algorithm_detector import PythonAlgorithmDetector
from app.infrastructure.llm.factory import build_llm_explainer
from app.infrastructure.parsing.python_ast_parser import PythonASTParser, PythonSyntaxError

router = APIRouter(prefix="/analyze", tags=["analyze"])


def get_analyze_use_case(settings: Settings = Depends(get_settings)) -> AnalyzeCodeUseCase:
    """
    Builds AnalyzeCodeUseCase with real adapters. Only Python is wired in
    for now (Milestone 3's scope) -- Tree-sitter-backed parsers for other
    languages will plug in here later without touching the use case itself.
    """
    return AnalyzeCodeUseCase(
        parser=PythonASTParser(),
        algorithm_detector=PythonAlgorithmDetector(),
        complexity_estimator=PythonComplexityEstimator(),
        explainer=build_llm_explainer(settings),
    )


@router.post("", response_model=AnalysisResult)
async def analyze_code(
    request: AnalyzeRequest,
    use_case: AnalyzeCodeUseCase = Depends(get_analyze_use_case),
) -> AnalysisResult:
    if request.language != Language.PYTHON:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Language '{request.language.value}' is not supported yet. "
                "Only Python is supported at this stage."
            ),
        )

    submission = CodeSubmission(source_code=request.source_code, language=request.language)

    try:
        return use_case.execute(submission)
    except PythonSyntaxError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc