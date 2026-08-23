from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.domain.entities import AnalysisHistoryEntry, User
from app.infrastructure.persistence.sqlalchemy_history_repository import (
    SqlAlchemyAnalysisHistoryRepository,
)

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[AnalysisHistoryEntry])
async def list_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnalysisHistoryEntry]:
    repo = SqlAlchemyAnalysisHistoryRepository(db)
    return repo.list_for_user(current_user.id)