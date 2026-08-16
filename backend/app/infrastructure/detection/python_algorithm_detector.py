"""
PythonAlgorithmDetector: the first real (non-fake) implementation of
AlgorithmDetectorPort.

"""

import ast

from app.application.dto import CodeGraph, FunctionInfo
from app.application.ports import AlgorithmDetectorPort
from app.domain.entities import AlgorithmMatch
from app.domain.enums import ConfidenceLevel

_LOW_NAMES = {"low", "left", "lo", "start"}
_HIGH_NAMES = {"high", "right", "hi", "end"}


class PythonAlgorithmDetector(AlgorithmDetectorPort):
    def detect(self, graph: CodeGraph) -> list[AlgorithmMatch]:
        matches: list[AlgorithmMatch] = []
        for func in graph.functions:
            if func.raw_node is None:
                continue
            matches.extend(self._detect_bubble_sort(func))
            matches.extend(self._detect_binary_search(func))
            matches.extend(self._detect_two_pointer(func))
        return matches

    # --- Bubble Sort -----------------------------------------------------

    def _detect_bubble_sort(self, func: FunctionInfo) -> list[AlgorithmMatch]:
        if len(func.loops) != 2 or func.max_nesting_depth != 2:
            return []
        if not self._has_adjacent_tuple_swap(func.raw_node):
            return []
        return [
            AlgorithmMatch(
                name="Bubble Sort",
                confidence=ConfidenceLevel.HIGH,
                location=func.location,
                rationale=(
                    "Two nested loops combined with an adjacent-element tuple swap "
                    "(e.g. arr[j], arr[j+1] = arr[j+1], arr[j]) — the defining "
                    "signature of Bubble Sort."
                ),
            )
        ]

    @staticmethod
    def _has_adjacent_tuple_swap(node: ast.AST) -> bool:
        for n in ast.walk(node):
            if (
                isinstance(n, ast.Assign)
                and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Tuple)
                and isinstance(n.value, ast.Tuple)
                and len(n.targets[0].elts) == 2
                and len(n.value.elts) == 2
            ):
                return True
        return False

    # --- Binary Search -----------------------------------------------------

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
                    "Single loop computing a midpoint as (low + high) // 2 and "
                    "reassigning a low/high-style boundary variable — matches "
                    "Binary Search's search-space-halving structure."
                ),
            )
        ]

    @staticmethod
    def _has_midpoint_halving(node: ast.AST) -> bool:
        has_mid_calc = False
        has_boundary_update = False

        for n in ast.walk(node):
            if (
                isinstance(n, ast.Assign)
                and isinstance(n.value, ast.BinOp)
                and isinstance(n.value.op, ast.FloorDiv)
                and isinstance(n.value.left, ast.BinOp)
                and isinstance(n.value.left.op, ast.Add)
                and isinstance(n.value.right, ast.Constant)
                and n.value.right.value == 2
            ):
                has_mid_calc = True

            if (
                isinstance(n, ast.Assign)
                and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id in (_LOW_NAMES | _HIGH_NAMES)
            ):
                has_boundary_update = True

        return has_mid_calc and has_boundary_update

    # --- Two Pointer -----------------------------------------------------

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

    @staticmethod
    def _find_converging_pointers(node: ast.AST) -> tuple[str, str] | None:
        incremented: set[str] = set()
        decremented: set[str] = set()

        for n in ast.walk(node):
            if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name):
                if isinstance(n.op, ast.Add):
                    incremented.add(n.target.id)
                elif isinstance(n.op, ast.Sub):
                    decremented.add(n.target.id)

        if incremented and decremented:
            return sorted(incremented)[0], sorted(decremented)[0]
        return None