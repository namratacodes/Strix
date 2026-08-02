import pytest
from pydantic import ValidationError

from app.domain.entities import AlgorithmMatch, CodeSubmission
from app.domain.enums import ComplexityClass, ConfidenceLevel, Language
from app.domain.value_objects import ComplexityEstimate


def test_complexity_class_ordering():
    assert ComplexityClass.O_1 < ComplexityClass.O_N
    assert ComplexityClass.O_N < ComplexityClass.O_N_SQUARED
    assert ComplexityClass.O_N_SQUARED < ComplexityClass.O_N_FACTORIAL


def test_complexity_estimate_requires_rationale():
    with pytest.raises(ValidationError):
        ComplexityEstimate(
            complexity_class=ComplexityClass.O_N,
            rationale="",  # empty rationale must be rejected
            confidence=ConfidenceLevel.HIGH,
        )


def test_complexity_estimate_is_immutable():
    estimate = ComplexityEstimate(
        complexity_class=ComplexityClass.O_N,
        rationale="Single loop over input",
        confidence=ConfidenceLevel.HIGH,
    )
    with pytest.raises(ValidationError):
        estimate.complexity_class = ComplexityClass.O_1  # type: ignore[misc]


def test_code_submission_generates_id_and_timestamp():
    submission = CodeSubmission(source_code="print(1)", language=Language.PYTHON)
    assert submission.id is not None
    assert submission.submitted_at is not None


def test_code_submission_rejects_empty_source():
    with pytest.raises(ValidationError):
        CodeSubmission(source_code="", language=Language.PYTHON)


def test_algorithm_match_requires_rationale_and_confidence():
    match = AlgorithmMatch(
        name="Binary Search",
        confidence=ConfidenceLevel.HIGH,
        rationale="Search space halves each iteration via mid-point comparison.",
    )
    assert match.location is None
