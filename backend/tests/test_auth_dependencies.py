"""
Tests get_optional_current_user / get_current_user directly, using a
simple stub in place of a real Starlette Request -- these dependencies
only ever touch `request.session`, so a stub with that one attribute is
sufficient. Google OAuth itself (login/callback against real Google
servers) isn't unit-testable here and is verified manually via browser.
"""

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.dependencies import get_current_user, get_optional_current_user
from app.core.database import Base
from app.infrastructure.persistence.sqlalchemy_user_repository import SqlAlchemyUserRepository


class FakeRequest:
    def __init__(self, session: dict):
        self.session = session


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def test_returns_none_without_session(db_session):
    result = get_optional_current_user(FakeRequest({}), db_session)
    assert result is None


def test_returns_user_when_session_has_valid_id(db_session):
    repo = SqlAlchemyUserRepository(db_session)
    user = repo.get_or_create_by_google_id("g-1", "a@b.com", "A")

    result = get_optional_current_user(FakeRequest({"user_id": str(user.id)}), db_session)

    assert result is not None
    assert result.id == user.id


def test_returns_none_for_unknown_user_id_in_session(db_session):
    result = get_optional_current_user(
        FakeRequest({"user_id": "00000000-0000-0000-0000-000000000000"}), db_session
    )
    assert result is None


def test_get_current_user_raises_401_when_not_authenticated():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(None)
    assert exc_info.value.status_code == 401


def test_get_current_user_returns_user_when_authenticated(db_session):
    repo = SqlAlchemyUserRepository(db_session)
    user = repo.get_or_create_by_google_id("g-2", "b@c.com", "B")
    result = get_current_user(user)
    assert result.id == user.id