from uuid import UUID

from sqlalchemy.orm import Session

from app.application.ports import AnalysisHistoryRepositoryPort
from app.domain.entities import AnalysisHistoryEntry, AnalysisResult
from app.infrastructure.persistence.models import AnalysisHistoryModel


class SqlAlchemyAnalysisHistoryRepository(AnalysisHistoryRepositoryPort):
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, entry: AnalysisHistoryEntry) -> AnalysisHistoryEntry:
        model = AnalysisHistoryModel(
            id=entry.id,
            user_id=entry.user_id,
            source_code=entry.source_code,
            language=entry.language.value,
            result_json=entry.result.model_dump(mode="json"),
            created_at=entry.created_at,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def list_for_user(self, user_id: UUID, limit: int = 20) -> list[AnalysisHistoryEntry]:
        models = (
            self._db.query(AnalysisHistoryModel)
            .filter_by(user_id=user_id)
            .order_by(AnalysisHistoryModel.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._to_domain(m) for m in models]

    @staticmethod
    def _to_domain(model: AnalysisHistoryModel) -> AnalysisHistoryEntry:
        return AnalysisHistoryEntry(
            id=model.id,
            user_id=model.user_id,
            source_code=model.source_code,
            language=model.language,
            result=AnalysisResult.model_validate(model.result_json),
            created_at=model.created_at,
        )