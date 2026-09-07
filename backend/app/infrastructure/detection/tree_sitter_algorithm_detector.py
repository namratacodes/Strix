"""
TreeSitterAlgorithmDetector: shared detection logic for Tree-sitter-backed
languages (C++, Java). Verified against both grammars: both expose
binary_expression with left/operator/right fields, assignment_expression,
declarations with an initializer, array/subscript access, and
update_expression for ++/-- -- close enough that one implementation
covers both languages, parameterized only by node-type-name differences.

Mirrors PythonAlgorithmDetector's 5 patterns exactly:
Bubble Sort, Binary Search, Two Pointer, Two Sum (Brute Force),
Duplicate Check (Brute Force). Same confidence/rationale discipline:
only fires on a genuine structural signature, never a guess.
"""

from tree_sitter import Node

from app.application.dto import CodeGraph, FunctionInfo
from app.application.ports import AlgorithmDetectorPort
from app.domain.entities import AlgorithmMatch
from app.domain.enums import ConfidenceLevel

_LOW_NAMES = {"low", "left", "lo", "start"}
_HIGH_NAMES = {"high", "right", "hi", "end"}

_DECLARATION_TYPES = {"declaration", "local_variable_declaration"}
_ASSIGNMENT_TYPES = {"assignment_expression"}
_ACCESS_TYPES = {"subscript_expression", "array_access"}
_UPDATE_TYPES = {"update_expression"}


class TreeSitterAlgorithmDetector(AlgorithmDetectorPort):
    def detect(self, graph: CodeGraph) -> list[AlgorithmMatch]:
        matches: list[AlgorithmMatch] = []
        for func in graph.functions:
            if func.raw_node is None:
                continue
            matches.extend(self._detect_bubble_sort(func))
            matches.extend(self._detect_binary_search(func))
            matches.extend(self._detect_two_pointer(func))
            matches.extend(self._detect_two_sum(func))
            matches.extend(self._detect_duplicate_check(func))
        return matches

    def _detect_bubble_sort(self, func: FunctionInfo) -> list[AlgorithmMatch]:
        if len(func.loops) != 2 or func.max_nesting_depth != 2:
            return []
        if not self._has_temp_swap(func.raw_node):
            return []
        return [
            AlgorithmMatch(
                name="Bubble Sort",
                confidence=ConfidenceLevel.HIGH,
                location=func.location,
                rationale=(
                    "Two nested loops combined with a temp-variable swap "
                    "(declaring a temp from one element, then reassigning "
                    "two array elements) — the defining signature of Bubble Sort."
                ),
            )
        ]

    def _has_temp_swap(self, node: Node) -> bool:
        has_temp_decl = False
        for n in self._walk(node):
            if n.type in _DECLARATION_TYPES and self._contains_access(n):
                has_temp_decl = True
                break
        if not has_temp_decl:
            return False
        assignment_count = sum(
            1
            for n in self._walk(node)
            if n.type in _ASSIGNMENT_TYPES and self._contains_access(n)
        )
        return assignment_count >= 2

    def _contains_access(self, node: Node) -> bool:
        return any(c.type in _ACCESS_TYPES for c in self._walk(node))

    def _detect_binary_search(self, func: FunctionInfo) -> list[AlgorithmMatch]:
        if len(func.loops) != 1 or func.max_nesting_depth != 1:
            return []
        if not self._has_midpoint_halving(func.raw_node):
            return []
        return [
            AlgorithmMatch(
                name="Binary Search",
                confidence=ConfidenceLevel.HIGH,
                location=func.location,
                rationale=(
                    "Single loop computing a midpoint as (low + high) / 2 "
                    "and reassigning a low/high-style boundary variable — "
                    "matches Binary Search's search-space-halving structure."
                ),
            )
        ]

    def _has_midpoint_halving(self, node: Node) -> bool:
        has_mid_calc = False
        has_boundary_update = False
        for n in self._walk(node):
            if n.type == "binary_expression":
                left = n.child_by_field_name("left")
                op = n.child_by_field_name("operator")
                right = n.child_by_field_name("right")
                if (
                    op is not None
                    and op.text == b"/"
                    and left is not None
                    and left.type == "parenthesized_expression"
                    and right is not None
                    and right.text in (b"2",)
                ):
                    inner = self._first_binary_child(left)
                    if inner is not None:
                        inner_op = inner.child_by_field_name("operator")
                        if inner_op is not None and inner_op.text == b"+":
                            has_mid_calc = True
            if n.type in _ASSIGNMENT_TYPES:
                left = n.child_by_field_name("left")
                if left is not None and left.type == "identifier":
                    name = left.text.decode("utf-8")
                    if name in (_LOW_NAMES | _HIGH_NAMES):
                        has_boundary_update = True
        return has_mid_calc and has_boundary_update

    @staticmethod
    def _first_binary_child(node: Node) -> Node | None:
        for c in node.children:
            if c.type == "binary_expression":
                return c
        return None

    def _detect_two_pointer(self, func: FunctionInfo) -> list[AlgorithmMatch]:
        if len(func.loops) != 1 or func.max_nesting_depth != 1:
            return []
        pointers = self._find_converging_pointers(func.raw_node)
        if pointers is None:
            return []
        incremented_name, decremented_name = pointers
        return [
            AlgorithmMatch(
                name="Two Pointer",
                confidence=ConfidenceLevel.MEDIUM,
                location=func.location,
                rationale=(
                    f"Single loop with two index variables ('{incremented_name}' "
                    f"incrementing, '{decremented_name}' decrementing) moving "
                    "toward each other — the Two Pointer pattern."
                ),
            )
        ]

    def _find_converging_pointers(self, node: Node) -> tuple[str, str] | None:
        incremented: set[str] = set()
        decremented: set[str] = set()
        for n in self._walk(node):
            if n.type in _UPDATE_TYPES:
                target = n.children[0] if n.children and n.children[0].type == "identifier" else None
                op_text = n.text.decode("utf-8")
                if target is not None:
                    name = target.text.decode("utf-8")
                    if "++" in op_text:
                        incremented.add(name)
                    elif "--" in op_text:
                        decremented.add(name)
        if incremented and decremented:
            return sorted(incremented)[0], sorted(decremented)[0]
        return None

    def _detect_two_sum(self, func: FunctionInfo) -> list[AlgorithmMatch]:
        if len(func.loops) != 2 or func.max_nesting_depth != 2:
            return []
        if not self._has_pair_sum_comparison(func.raw_node):
            return []
        return [
            AlgorithmMatch(
                name="Two Sum (Brute Force)",
                confidence=ConfidenceLevel.HIGH,
                location=func.location,
                rationale=(
                    "Two nested loops with a comparison of the form "
                    "'a + b == target' — the classic brute-force Two Sum "
                    "signature, checking every pair for a matching sum."
                ),
            )
        ]

    def _has_pair_sum_comparison(self, node: Node) -> bool:
        for n in self._walk(node):
            if n.type != "binary_expression":
                continue
            op = n.child_by_field_name("operator")
            if op is None or op.text != b"==":
                continue
            left = n.child_by_field_name("left")
            right = n.child_by_field_name("right")
            for side in (left, right):
                if side is not None and side.type == "binary_expression":
                    side_op = side.child_by_field_name("operator")
                    if side_op is not None and side_op.text == b"+":
                        return True
        return False

    def _detect_duplicate_check(self, func: FunctionInfo) -> list[AlgorithmMatch]:
        if len(func.loops) != 2 or func.max_nesting_depth != 2:
            return []
        if not self._has_element_equality_comparison(func.raw_node):
            return []
        return [
            AlgorithmMatch(
                name="Duplicate Check (Brute Force)",
                confidence=ConfidenceLevel.HIGH,
                location=func.location,
                rationale=(
                    "Two nested loops comparing indexed elements for "
                    "equality (e.g. arr[i] == arr[j]) — the brute-force "
                    "signature for checking whether any two elements match."
                ),
            )
        ]

    def _has_element_equality_comparison(self, node: Node) -> bool:
        for n in self._walk(node):
            if n.type != "binary_expression":
                continue
            op = n.child_by_field_name("operator")
            if op is None or op.text != b"==":
                continue
            left = n.child_by_field_name("left")
            right = n.child_by_field_name("right")
            if (
                left is not None
                and right is not None
                and left.type in _ACCESS_TYPES
                and right.type in _ACCESS_TYPES
            ):
                return True
        return False

    @staticmethod
    def _walk(node: Node):
        yield node
        for child in node.children:
            yield from TreeSitterAlgorithmDetector._walk(child)