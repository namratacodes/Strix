from app.infrastructure.complexity.python_complexity_estimator import (
    PythonComplexityEstimator,
)
from app.infrastructure.parsing.python_ast_parser import PythonASTParser

parser = PythonASTParser()
estimator = PythonComplexityEstimator()


def _estimate(source: str):
    graph = parser.parse(source)
    return estimator.estimate(graph)


def test_constant_time_no_loops_no_recursion():
    source = """
def add(a, b):
    return a + b
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(1)"
    assert result.space.complexity_class.value == "O(1)"


def test_single_loop_is_linear():
    source = """
def total(items):
    result = 0
    for item in items:
        result += item
    return result
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(n)"
    assert result.worst_case.confidence.value == "high"


def test_nested_loops_are_quadratic():
    source = """
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(n^2)"
    assert result.worst_case.confidence.value == "high"
    # In-place swap, no growing collection -> constant space
    assert result.space.complexity_class.value == "O(1)"


def test_binary_search_style_loop_is_logarithmic():
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
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(log n)"


def test_linear_recursion_is_linear_time_and_space():
    source = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(n)"
    assert result.space.complexity_class.value == "O(n)"
    assert result.space.confidence.value == "high"


def test_branching_recursion_is_exponential():
    source = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
"""
    result = _estimate(source)
    assert result.worst_case.complexity_class.value == "O(2^n)"
    # Call-stack depth is still linear even though total calls are exponential
    assert result.space.complexity_class.value == "O(n)"


def test_growing_collection_flags_linear_space():
    source = """
def squares(items):
    result = []
    for item in items:
        result.append(item * item)
    return result
"""
    result = _estimate(source)
    assert result.space.complexity_class.value == "O(n)"
    assert result.space.confidence.value == "medium"


def test_triple_nested_loop_is_conservative_lower_bound():
    source = """
def cube_sum(n):
    total = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                total += i * j * k
    return total
"""
    result = _estimate(source)
    # Not O(n^3) -- our scale doesn't go there -- but a HONEST, LOW-confidence
    # lower bound of O(n^2), not a fabricated precise class.
    assert result.worst_case.complexity_class.value == "O(n^2)"
    assert result.worst_case.confidence.value == "low"


def test_best_average_worst_are_currently_uniform():
    source = """
def total(items):
    result = 0
    for item in items:
        result += item
    return result
"""
    result = _estimate(source)
    assert result.best_case == result.average_case == result.worst_case