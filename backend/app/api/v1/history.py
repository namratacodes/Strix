from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.domain.entities import AnalysisHistoryEntry, User
from app.infrastructure.persistence.sqlalchemy_history_repository import (
    SqlAlchemyAnalysisHistoryRepository,
)

router = APIRouter(prefix="/history", tags=["history"])


class UpdateHistoryRequest(BaseModel):
    is_pinned: bool | None = None
    label: str | None = None


@router.get("", response_model=list[AnalysisHistoryEntry])
async def list_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AnalysisHistoryEntry]:
    repo = SqlAlchemyAnalysisHistoryRepository(db)
    return repo.list_for_user(current_user.id)


@router.patch("/{entry_id}", response_model=AnalysisHistoryEntry)
async def update_history_entry(
    entry_id: UUID,
    request: UpdateHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisHistoryEntry:
    repo = SqlAlchemyAnalysisHistoryRepository(db)
    updated = repo.update(
        entry_id, current_user.id, is_pinned=request.is_pinned, label=request.label
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found.")
    return updated