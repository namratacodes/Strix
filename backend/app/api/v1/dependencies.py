from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.entities import User
from app.infrastructure.persistence.sqlalchemy_user_repository import SqlAlchemyUserRepository


def get_optional_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    repo = SqlAlchemyUserRepository(db)
    return repo.get_by_id(UUID(user_id))


def get_current_user(user: User | None = Depends(get_optional_current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    return user