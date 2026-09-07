from app.infrastructure.detection.python_algorithm_detector import PythonAlgorithmDetector
from app.infrastructure.optimization.rule_based_optimizer import RuleBasedOptimizer
from app.infrastructure.parsing.python_ast_parser import PythonASTParser

parser = PythonASTParser()
detector = PythonAlgorithmDetector()
optimizer = RuleBasedOptimizer()


def test_detects_two_sum_brute_force():
    source = """
def two_sum(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return [-1, -1]
"""
    graph = parser.parse(source)
    matches = detector.detect(graph)
    names = [m.name for m in matches]
    assert "Two Sum (Brute Force)" in names

    suggestions = optimizer.suggest(matches, None)
    titles = [s.title for s in suggestions]
    assert "Replace brute-force Two Sum with a hash map" in titles


def test_detects_duplicate_check_brute_force():
    source = """
def has_duplicate_pair(arr):
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j and arr[i] == arr[j]:
                return True
    return False
"""
    graph = parser.parse(source)
    matches = detector.detect(graph)
    names = [m.name for m in matches]
    assert "Duplicate Check (Brute Force)" in names

    suggestions = optimizer.suggest(matches, None)
    titles = [s.title for s in suggestions]
    assert "Replace brute-force duplicate check with a set" in titles


def test_bubble_sort_not_confused_with_two_sum_or_duplicate_check():
    source = """
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
"""
    graph = parser.parse(source)
    matches = detector.detect(graph)
    names = [m.name for m in matches]
    assert "Two Sum (Brute Force)" not in names
    assert "Duplicate Check (Brute Force)" not in names
    assert "Bubble Sort" in names