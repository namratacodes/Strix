from uuid import UUID

from sqlalchemy.orm import Session

from app.application.ports import UserRepositoryPort
from app.domain.entities import User
from app.infrastructure.persistence.models import UserModel


class SqlAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_or_create_by_google_id(self, google_id: str, email: str, display_name: str) -> User:
        existing = self._db.query(UserModel).filter_by(google_id=google_id).one_or_none()
        if existing:
            return self._to_domain(existing)

        model = UserModel(google_id=google_id, email=email, display_name=display_name)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self._db.query(UserModel).filter_by(id=user_id).one_or_none()
        return self._to_domain(model) if model else None

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            google_id=model.google_id,
            email=model.email,
            display_name=model.display_name,
            created_at=model.created_at,
        )