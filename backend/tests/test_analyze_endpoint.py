"""
Integration tests for POST /api/v1/analyze.

Deliberately run against the REAL pipeline (real parser, real detector,
real complexity estimator, real explainer chain) rather than mocks --
these are end-to-end tests of the actual composition root. Note that
these pass even with NO Ollama instance running: Milestone 7's
ResilientExplainer transparently falls back to TemplateExplainer, so the
endpoint never fails just because the LLM backend is unavailable.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_detects_bubble_sort_end_to_end():
    source = """
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
"""
    response = client.post("/api/v1/analyze", json={"source_code": source, "language": "python"})

    assert response.status_code == 200
    body = response.json()

    algo_names = [m["name"] for m in body["algorithm_matches"]]
    assert "Bubble Sort" in algo_names
    assert body["complexity"]["worst_case"]["complexity_class"] == "O(n^2)"
    assert len(body["reasoning_timeline"]) == 8
    assert body["explanation"]


def test_analyze_defaults_to_python_language():
    response = client.post("/api/v1/analyze", json={"source_code": "x = 1"})
    assert response.status_code == 200


def test_analyze_rejects_unsupported_language():
    response = client.post(
        "/api/v1/analyze", json={"source_code": "console.log(1)", "language": "javascript"}
    )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]


def test_analyze_rejects_invalid_python_syntax():
    response = client.post(
        "/api/v1/analyze", json={"source_code": "def broken(:\n    pass", "language": "python"}
    )
    assert response.status_code == 400
    assert "Invalid Python syntax" in response.json()["detail"]


def test_analyze_rejects_empty_source_code():
    response = client.post("/api/v1/analyze", json={"source_code": "", "language": "python"})
    assert response.status_code == 422


def test_analyze_binary_search_returns_log_n():
    source = """
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""
    response = client.post("/api/v1/analyze", json={"source_code": source, "language": "python"})
    assert response.status_code == 200
    body = response.json()
    assert body["complexity"]["worst_case"]["complexity_class"] == "O(log n)"