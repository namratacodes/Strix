from app.infrastructure.detection.tree_sitter_algorithm_detector import (
    TreeSitterAlgorithmDetector,
)
from app.infrastructure.parsing.java_ast_parser import JavaASTParser

parser = JavaASTParser()
detector = TreeSitterAlgorithmDetector()


def _detect(source: str):
    graph = parser.parse(source)
    return detector.detect(graph)


def test_detects_bubble_sort_java():
    source = """
public class S {
    void bubbleSort(int[] arr, int n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - 1; j++) {
                if (arr[j] > arr[j+1]) {
                    int temp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = temp;
                }
            }
        }
    }
}
"""
    names = [m.name for m in _detect(source)]
    assert "Bubble Sort" in names


def test_detects_binary_search_java():
    source = """
public class S {
    int binarySearch(int[] arr, int n, int target) {
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
}
"""
    names = [m.name for m in _detect(source)]
    assert "Binary Search" in names


def test_detects_two_pointer_java():
    source = """
public class S {
    boolean isPalindrome(char[] s, int n) {
        int left = 0;
        int right = n - 1;
        while (left < right) {
            if (s[left] != s[right]) return false;
            left++;
            right--;
        }
        return true;
    }
}
"""
    names = [m.name for m in _detect(source)]
    assert "Two Pointer" in names


def test_detects_two_sum_java():
    source = """
public class S {
    int[] twoSum(int[] nums, int n, int target) {
        for (int i = 0; i < n; i++) {
            for (int j = i+1; j < n; j++) {
                if (nums[i] + nums[j] == target) return new int[]{i, j};
            }
        }
        return null;
    }
}
"""
    names = [m.name for m in _detect(source)]
    assert "Two Sum (Brute Force)" in names


def test_detects_duplicate_check_java():
    source = """
public class S {
    boolean hasDup(int[] arr, int n) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i != j && arr[i] == arr[j]) return true;
            }
        }
        return false;
    }
}
"""
    names = [m.name for m in _detect(source)]
    assert "Duplicate Check (Brute Force)" in names


def test_does_not_falsely_match_plain_grid_loop_java():
    source = """
public class S {
    void printGrid(int rows, int cols) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                System.out.println(i);
            }
        }
    }
}
"""
    assert _detect(source) == []