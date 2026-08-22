from app.infrastructure.complexity.python_complexity_estimator import (
    PythonComplexityEstimator,
)
from app.infrastructure.parsing.python_ast_parser import PythonASTParser

parser = PythonASTParser()
estimator = PythonComplexityEstimator()


def _estimate(source: str):
    graph = parser.parse(source)
    return estimator.estimate(graph)


def test_bisect_call_detected_as_log_n():
    source = """
import bisect

def binary_search_builtin(arr, target):
    index = bisect.bisect_left(arr, target)
    if index < len(arr) and arr[index] == target:
        return index
    return -1
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(log n)"
    assert result.worst_case.confidence.value == "medium"
    assert "bisect_left" in result.worst_case.rationale


def test_sorted_call_detected_as_n_log_n():
    source = """
def get_sorted(items):
    return sorted(items)
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(n log n)"


def test_no_builtin_and_no_loops_still_constant():
    source = """
def add(a, b):
    return a + b
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(1)"
    assert result.worst_case.confidence.value == "high"


def test_user_loop_takes_precedence_over_builtin_call():
    # Even though sorted() is called, the explicit user loop should win
    # since it's directly analyzed, not inferred from a builtin's reputation.
    source = """
def process(items):
    result = sorted(items)
    for item in result:
        for other in result:
            print(item, other)
    return result
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(n^2)"