import pytest

from app.infrastructure.parsing.java_ast_parser import JavaASTParser, JavaSyntaxError

parser = JavaASTParser()


def test_supported_language_is_java():
    assert parser.supported_language.value == "java"


def test_detects_nested_loops_in_a_method():
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
    graph = parser.parse(source)
    assert len(graph.functions) == 1
    func = graph.functions[0]
    assert func.name == "bubbleSort"
    assert len(func.loops) == 2
    assert func.max_nesting_depth == 2
    assert func.is_recursive is False


def test_detects_linear_recursion():
    source = """
public class Solution {
    public static int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
}
"""
    graph = parser.parse(source)
    func = graph.functions[0]
    assert func.is_recursive is True
    assert func.self_call_count == 1


def test_detects_branching_recursion():
    source = """
public class Solution {
    public static int fib(int n) {
        if (n <= 1) return n;
        return fib(n - 1) + fib(n - 2);
    }
}
"""
    graph = parser.parse(source)
    func = graph.functions[0]
    assert func.self_call_count == 2


def test_multiple_methods_in_one_class():
    source = """
public class Solution {
    public static int add(int a, int b) {
        return a + b;
    }

    public static int multiply(int a, int b) {
        return a * b;
    }
}
"""
    graph = parser.parse(source)
    names = sorted(f.name for f in graph.functions)
    assert names == ["add", "multiply"]


def test_invalid_java_raises_domain_exception():
    with pytest.raises(JavaSyntaxError):
        parser.parse("public class {{{ broken ]]]")