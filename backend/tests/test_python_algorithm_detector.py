from app.infrastructure.detection.python_algorithm_detector import PythonAlgorithmDetector
from app.infrastructure.parsing.python_ast_parser import PythonASTParser

parser = PythonASTParser()
detector = PythonAlgorithmDetector()


def _detect(source: str):
    graph = parser.parse(source)
    return detector.detect(graph)


def test_detects_bubble_sort():
    source = """
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    matches = _detect(source)
    names = [m.name for m in matches]
    assert "Bubble Sort" in names
    match = next(m for m in matches if m.name == "Bubble Sort")
    assert match.confidence.value == "high"
    assert match.rationale


def test_detects_binary_search():
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
    matches = _detect(source)
    names = [m.name for m in matches]
    assert "Binary Search" in names
    match = next(m for m in matches if m.name == "Binary Search")
    assert match.confidence.value == "high"


def test_detects_two_pointer():
    source = """
def is_palindrome(s):
    left = 0
    right = len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
"""
    matches = _detect(source)
    names = [m.name for m in matches]
    assert "Two Pointer" in names


def test_does_not_falsely_match_unrelated_nested_loops():
    source = """
def print_grid(rows, cols):
    for i in range(rows):
        for j in range(cols):
            print(i, j)
"""
    matches = _detect(source)
    assert matches == []


def test_does_not_falsely_match_simple_linear_search():
    source = """
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
"""
    matches = _detect(source)
    # No mid-calculation, no swap, no converging pointers -> nothing detected
    assert matches == []