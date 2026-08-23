"""
Tests the persistence layer against in-memory SQLite rather than a live
Neon Postgres connection -- proves the repository logic (queries, domain
<-> ORM translation) is correct without needing real database credentials
in this environment. Production still uses real Postgres via DATABASE_URL.
"""

from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.domain.entities import AlgorithmMatch, AnalysisHistoryEntry, AnalysisResult, ComplexityResult
from app.domain.enums import ConfidenceLevel, Language
from app.domain.value_objects import ComplexityEstimate
from app.infrastructure.persistence.sqlalchemy_history_repository import (
    SqlAlchemyAnalysisHistoryRepository,
)
from app.infrastructure.persistence.sqlalchemy_user_repository import SqlAlchemyUserRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def _sample_result() -> AnalysisResult:
    estimate = ComplexityEstimate(complexity_class="O(n)", rationale="x", confidence=ConfidenceLevel.HIGH)
    return AnalysisResult(
        submission_id=UUID("11111111-1111-1111-1111-111111111111"),
        algorithm_matches=[AlgorithmMatch(name="Linear Scan", confidence=ConfidenceLevel.HIGH, rationale="x")],
        complexity=ComplexityResult(best_case=estimate, average_case=estimate, worst_case=estimate, space=estimate),
        reasoning_timeline=[],
        explanation="test explanation",
    )


def test_creates_user_on_first_login(db_session: Session):
    repo = SqlAlchemyUserRepository(db_session)
    user = repo.get_or_create_by_google_id("google-123", "test@example.com", "Test User")
    assert user.google_id == "google-123"
    assert user.email == "test@example.com"


def test_returns_same_user_on_second_login(db_session: Session):
    repo = SqlAlchemyUserRepository(db_session)
    first = repo.get_or_create_by_google_id("google-123", "test@example.com", "Test User")
    second = repo.get_or_create_by_google_id("google-123", "test@example.com", "Test User")
    assert first.id == second.id


def test_get_by_id_returns_none_for_unknown_user(db_session: Session):
    repo = SqlAlchemyUserRepository(db_session)
    assert repo.get_by_id(UUID("00000000-0000-0000-0000-000000000000")) is None


def test_saves_and_lists_history_for_user(db_session: Session):
    user_repo = SqlAlchemyUserRepository(db_session)
    history_repo = SqlAlchemyAnalysisHistoryRepository(db_session)

    user = user_repo.get_or_create_by_google_id("google-abc", "a@b.com", "A")
    entry = AnalysisHistoryEntry(
        user_id=user.id,
        source_code="def f(): pass",
        language=Language.PYTHON,
        result=_sample_result(),
    )
    saved = history_repo.save(entry)
    assert saved.id == entry.id

    history = history_repo.list_for_user(user.id)
    assert len(history) == 1
    assert history[0].source_code == "def f(): pass"
    assert history[0].result.explanation == "test explanation"


def test_history_is_scoped_per_user(db_session: Session):
    user_repo = SqlAlchemyUserRepository(db_session)
    history_repo = SqlAlchemyAnalysisHistoryRepository(db_session)

    user_a = user_repo.get_or_create_by_google_id("google-a", "a@x.com", "A")
    user_b = user_repo.get_or_create_by_google_id("google-b", "b@x.com", "B")

    history_repo.save(
        AnalysisHistoryEntry(
            user_id=user_a.id, source_code="a", language=Language.PYTHON, result=_sample_result()
        )
    )

    assert len(history_repo.list_for_user(user_a.id)) == 1
    assert len(history_repo.list_for_user(user_b.id)) == 0