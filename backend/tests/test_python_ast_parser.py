import pytest

from app.infrastructure.parsing.python_ast_parser import (
    PythonASTParser,
    PythonSyntaxError,
)

parser = PythonASTParser()


def test_supported_language_is_python():
    assert parser.supported_language.value == "python"


def test_detects_single_loop_at_top_level():
    source = """
for i in range(10):
    print(i)
"""
    graph = parser.parse(source)
    assert len(graph.top_level_loops) == 1
    assert graph.top_level_loops[0].loop_type == "for"
    assert graph.top_level_loops[0].nesting_depth == 1


def test_detects_nested_loops_and_their_depth():
    source = """
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
"""
    graph = parser.parse(source)
    assert len(graph.functions) == 1
    func = graph.functions[0]
    assert func.name == "bubble_sort"
    assert len(func.loops) == 2
    assert func.max_nesting_depth == 2
    assert sorted(loop.nesting_depth for loop in func.loops) == [1, 2]


def test_detects_direct_recursion():
    source = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    graph = parser.parse(source)
    func = graph.functions[0]
    assert func.is_recursive is True
    assert "factorial" in func.calls


def test_non_recursive_function_is_flagged_correctly():
    source = """
def add(a, b):
    return a + b
"""
    graph = parser.parse(source)
    func = graph.functions[0]
    assert func.is_recursive is False
    assert func.loops == ()


def test_loop_inside_nested_function_not_attributed_to_outer_function():
    source = """
def outer():
    def inner():
        for i in range(5):
            pass
    return 1
"""
    graph = parser.parse(source)
    outer_func = next(f for f in graph.functions if f.name == "outer")
    # The loop belongs to `inner`, a nested function we don't break out
    # separately yet (documented scope cut) -- but it must NOT be
    # miscounted as belonging to `outer`.
    assert outer_func.loops == ()


def test_invalid_python_raises_domain_exception():
    with pytest.raises(PythonSyntaxError):
        parser.parse("def broken(:\n    pass")


def test_calls_are_collected_and_sorted():
    source = """
def process():
    validate()
    transform()
    validate()
"""
    graph = parser.parse(source)
    func = graph.functions[0]
    assert func.calls == ("transform", "validate")