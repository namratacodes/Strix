"""
Integration tests proving C++ works end-to-end through the real
/analyze endpoint -- run against the actual composition root, not mocks.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_cpp_bubble_sort_returns_quadratic():
    source = """
int bubbleSort(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - 1; j++) {
            if (arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
    return 0;
}
"""
    response = client.post("/api/v1/analyze", json={"source_code": source, "language": "cpp"})
    assert response.status_code == 200
    body = response.json()
    assert body["complexity"]["worst_case"]["complexity_class"] == "O(n^2)"
    algo_names = [m["name"] for m in body["algorithm_matches"]]
    assert "Bubble Sort" in algo_names


def test_analyze_cpp_recursive_factorial_returns_linear():
    source = """
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
"""
    response = client.post("/api/v1/analyze", json={"source_code": source, "language": "cpp"})
    assert response.status_code == 200
    body = response.json()
    assert body["complexity"]["worst_case"]["complexity_class"] == "O(n)"
    assert body["complexity"]["space"]["complexity_class"] == "O(n)"


def test_analyze_cpp_rejects_invalid_syntax():
    response = client.post(
        "/api/v1/analyze", json={"source_code": "int broken(( {{{ ]]]", "language": "cpp"}
    )
    assert response.status_code == 400


def test_analyze_still_rejects_unsupported_language():
    response = client.post(
        "/api/v1/analyze", json={"source_code": "console.log(1)", "language": "javascript"}
    )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]