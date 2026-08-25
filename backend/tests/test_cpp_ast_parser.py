import pytest

from app.infrastructure.parsing.cpp_ast_parser import CppASTParser, CppSyntaxError

parser = CppASTParser()


def test_supported_language_is_cpp():
    assert parser.supported_language.value == "cpp"


def test_detects_nested_loops_and_recursion_correctly():
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
    graph = parser.parse(source)
    assert len(graph.functions) == 1
    func = graph.functions[0]
    assert func.name == "bubbleSort"
    assert len(func.loops) == 2
    assert func.max_nesting_depth == 2
    assert func.is_recursive is False


def test_detects_linear_recursion():
    source = """
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
"""
    graph = parser.parse(source)
    func = graph.functions[0]
    assert func.is_recursive is True
    assert func.self_call_count == 1


def test_detects_branching_recursion():
    source = """
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
"""
    graph = parser.parse(source)
    func = graph.functions[0]
    assert func.self_call_count == 2


def test_single_loop_binary_search():
    source = """
int binarySearch(int arr[], int n, int target) {
    int low = 0;
    int high = n - 1;
    while (low <= high) {
        int mid = (low + high) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}
"""
    graph = parser.parse(source)
    func = graph.functions[0]
    assert len(func.loops) == 1
    assert func.loops[0].loop_type == "while"
    assert func.max_nesting_depth == 1


def test_invalid_cpp_raises_domain_exception():
    with pytest.raises(CppSyntaxError):
        parser.parse("int broken(( {{{ ]]]")