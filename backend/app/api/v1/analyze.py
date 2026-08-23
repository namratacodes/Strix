"""
The /analyze endpoint: STRIX's core API surface.

This is the ONE file in the codebase allowed to import concrete
infrastructure classes (PythonASTParser, PythonAlgorithmDetector, etc.)
alongside the application-layer use case -- it's the composition root
where abstract ports get wired to real adapters via FastAPI's dependency
injection. Every other file depends only on ports.

History saving (Milestone 10b) is intentionally a silent side effect:
logged-out users get the full analysis with no behavior change; logged-in
users additionally get it saved. No API contract change either way.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_optional_current_user
from app.api.v1.schemas import AnalyzeRequest
from app.application.use_cases.analyze_code import AnalyzeCodeUseCase
from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.domain.entities import AnalysisHistoryEntry, AnalysisResult, CodeSubmission, User
from app.domain.enums import Language
from app.infrastructure.complexity.python_complexity_estimator import (
    PythonComplexityEstimator,
)
from app.infrastructure.detection.python_algorithm_detector import PythonAlgorithmDetector
from app.infrastructure.llm.factory import build_llm_explainer
from app.infrastructure.parsing.python_ast_parser import PythonASTParser, PythonSyntaxError
from app.infrastructure.persistence.sqlalchemy_history_repository import (
    SqlAlchemyAnalysisHistoryRepository,
)

router = APIRouter(prefix="/analyze", tags=["analyze"])


def get_analyze_use_case(settings: Settings = Depends(get_settings)) -> AnalyzeCodeUseCase:
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
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
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
        result = use_case.execute(submission)
    except PythonSyntaxError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if current_user is not None:
        history_repo = SqlAlchemyAnalysisHistoryRepository(db)
        history_repo.save(
            AnalysisHistoryEntry(
                user_id=current_user.id,
                source_code=request.source_code,
                language=request.language,
                result=result,
            )
        )

    return result