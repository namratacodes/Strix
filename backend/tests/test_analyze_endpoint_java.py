from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_java_bubble_sort_returns_quadratic():
    source = """
public class Solution {
    public static int[] bubbleSort(int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            for (int j = 0; j < arr.length - 1; j++) {
                if (arr[j] > arr[j+1]) {
                    int temp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = temp;
                }
            }
        }
        return arr;
    }
}
"""
    response = client.post("/api/v1/analyze", json={"source_code": source, "language": "java"})
    assert response.status_code == 200
    body = response.json()
    assert body["complexity"]["worst_case"]["complexity_class"] == "O(n^2)"
    algo_names = [m["name"] for m in body["algorithm_matches"]]
    assert "Bubble Sort" in algo_names


def test_analyze_java_recursive_factorial_returns_linear():
    source = """
public class Solution {
    public static int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
}
"""
    response = client.post("/api/v1/analyze", json={"source_code": source, "language": "java"})
    assert response.status_code == 200
    body = response.json()
    assert body["complexity"]["worst_case"]["complexity_class"] == "O(n)"
    assert body["complexity"]["space"]["complexity_class"] == "O(n)"


def test_analyze_java_rejects_invalid_syntax():
    response = client.post(
        "/api/v1/analyze", json={"source_code": "public class {{{ broken ]]]", "language": "java"}
    )
    assert response.status_code == 400