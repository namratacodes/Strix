"""
The /analyze endpoint: STRIX's core API surface.

This is the ONE file in the codebase allowed to import concrete
infrastructure classes alongside the application-layer use case -- it's
the composition root where abstract ports get wired to real adapters via
FastAPI's dependency injection. Every other file depends only on ports.

Language dispatch (Milestone 12) goes through
infrastructure/language_support.py's factory functions rather than a
hardcoded if/else here -- this file doesn't need to know HOW MANY
languages are supported, only whether the requested one is.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_optional_current_user
from app.api.v1.schemas import AnalyzeRequest
from app.application.use_cases.analyze_code import AnalyzeCodeUseCase
from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.domain.entities import AnalysisHistoryEntry, AnalysisResult, CodeSubmission, User
from app.infrastructure.language_support import (
    build_algorithm_detector,
    build_complexity_estimator,
    build_parser,
    is_language_supported,
)
from app.infrastructure.llm.factory import build_llm_explainer
from app.infrastructure.parsing.cpp_ast_parser import CppSyntaxError
from app.infrastructure.parsing.java_ast_parser import JavaSyntaxError
from app.infrastructure.parsing.python_ast_parser import PythonSyntaxError
from app.infrastructure.persistence.sqlalchemy_history_repository import (
    SqlAlchemyAnalysisHistoryRepository,
)
from app.infrastructure.optimization.rule_based_optimizer import RuleBasedOptimizer

router = APIRouter(prefix="/analyze", tags=["analyze"])

_PARSER_ERRORS = (PythonSyntaxError, CppSyntaxError, JavaSyntaxError)


def get_analyze_use_case(
    request: AnalyzeRequest, settings: Settings = Depends(get_settings)
) -> AnalyzeCodeUseCase:
    if not is_language_supported(request.language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Language '{request.language.value}' is not supported yet. "
                "Currently supported: Python, C++."
            ),
        )
    return AnalyzeCodeUseCase(
        parser=build_parser(request.language),
        algorithm_detector=build_algorithm_detector(request.language),
        complexity_estimator=build_complexity_estimator(request.language),
        explainer=build_llm_explainer(settings),
        optimizer=RuleBasedOptimizer(),
    )


@router.post("", response_model=AnalysisResult)
async def analyze_code(
    request: AnalyzeRequest,
    use_case: AnalyzeCodeUseCase = Depends(get_analyze_use_case),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> AnalysisResult:
    submission = CodeSubmission(source_code=request.source_code, language=request.language)

    try:
        result = use_case.execute(submission)
    except _PARSER_ERRORS as exc:
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