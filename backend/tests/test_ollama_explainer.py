from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.domain.entities import AlgorithmMatch, ComplexityResult
from app.domain.enums import ConfidenceLevel
from app.domain.value_objects import ComplexityEstimate
from app.infrastructure.llm.ollama_explainer import OllamaExplainer, OllamaExplainerError

explainer = OllamaExplainer(base_url="http://localhost:11434", model="qwen2.5-coder")


def _estimate(cls="O(n)"):
    return ComplexityEstimate(complexity_class=cls, rationale="x", confidence=ConfidenceLevel.HIGH)


def _complexity():
    return ComplexityResult(
        best_case=_estimate("O(n^2)"),
        average_case=_estimate("O(n^2)"),
        worst_case=_estimate("O(n^2)"),
        space=_estimate("O(1)"),
    )


def test_returns_response_text_on_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "This code sorts using Bubble Sort."}
    mock_response.raise_for_status.return_value = None

    with patch("app.infrastructure.llm.ollama_explainer.httpx.post", return_value=mock_response) as mock_post:
        match = AlgorithmMatch(name="Bubble Sort", confidence=ConfidenceLevel.HIGH, rationale="x")
        text = explainer.explain([match], _complexity())

    assert text == "This code sorts using Bubble Sort."
    call_kwargs = mock_post.call_args.kwargs
    assert "Bubble Sort" in call_kwargs["json"]["prompt"]
    assert "O(n^2)" in call_kwargs["json"]["prompt"]
    assert call_kwargs["json"]["model"] == "qwen2.5-coder"


def test_raises_on_connection_failure():
    with patch(
        "app.infrastructure.llm.ollama_explainer.httpx.post",
        side_effect=httpx.ConnectError("connection refused"),
    ):
        with pytest.raises(OllamaExplainerError):
            explainer.explain([], _complexity())


def test_raises_on_empty_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "   "}
    mock_response.raise_for_status.return_value = None

    with patch("app.infrastructure.llm.ollama_explainer.httpx.post", return_value=mock_response):
        with pytest.raises(OllamaExplainerError):
            explainer.explain([], _complexity())


def test_prompt_states_no_match_explicitly_when_none_found():
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "No known pattern found."}
    mock_response.raise_for_status.return_value = None

    with patch("app.infrastructure.llm.ollama_explainer.httpx.post", return_value=mock_response) as mock_post:
        explainer.explain([], _complexity())

    prompt = mock_post.call_args.kwargs["json"]["prompt"]
    assert "No algorithm pattern was confidently matched" in prompt