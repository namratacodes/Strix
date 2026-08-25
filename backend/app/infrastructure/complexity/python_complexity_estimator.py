"""
PythonComplexityEstimator: adds Python-specific pattern recognition on
top of BaseComplexityEstimator's language-agnostic decision tree --
recognizing O(log n) midpoint-halving loops, growing collections, and
known standard-library functions with textbook complexity (e.g. bisect,
sorted). These three hooks are the only Python-specific code in the
entire complexity estimation pipeline.
"""

import ast

from app.domain.enums import ComplexityClass, ConfidenceLevel
from app.domain.value_objects import ComplexityEstimate
from app.infrastructure.complexity.base_complexity_estimator import BaseComplexityEstimator

_LOW_NAMES = {"low", "left", "lo", "start"}
_HIGH_NAMES = {"high", "right", "hi", "end"}
_MUTATING_METHODS = {"append", "add", "update", "extend", "insert"}

# Well-known standard-library / builtin functions with textbook complexity.
# Recognized by name only (not verified for correct usage, e.g. calling
# bisect on an unsorted list still matches here) -- fills a real gap:
# STRIX can't see inside a builtin's C implementation, so it falls back
# to the function's documented complexity instead of wrongly defaulting
# to O(1).
_BUILTIN_COMPLEXITY: dict[str, ComplexityClass] = {
    "bisect_left": ComplexityClass.O_LOG_N,
    "bisect_right": ComplexityClass.O_LOG_N,
    "bisect": ComplexityClass.O_LOG_N,
    "sorted": ComplexityClass.O_N_LOG_N,
    "sort": ComplexityClass.O_N_LOG_N,
    "max": ComplexityClass.O_N,
    "min": ComplexityClass.O_N,
    "sum": ComplexityClass.O_N,
    "reversed": ComplexityClass.O_N,
    "count": ComplexityClass.O_N,
    "index": ComplexityClass.O_N,
}


class PythonComplexityEstimator(BaseComplexityEstimator):
    def _has_midpoint_halving(self, node: ast.AST | None) -> bool:
        if node is None:
            return False
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

    def _has_growing_collection(self, node: ast.AST | None) -> bool:
        if node is None:
            return False
        for n in ast.walk(node):
            if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                return True
            if (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr in _MUTATING_METHODS
            ):
                return True
        return False

    def _estimate_from_builtins(self, node: ast.AST | None) -> ComplexityEstimate | None:
        if node is None:
            return None
        matched: list[tuple[str, ComplexityClass]] = []
        for n in ast.walk(node):
            if not isinstance(n, ast.Call):
                continue
            name = self._call_name(n)
            if name and name in _BUILTIN_COMPLEXITY:
                matched.append((name, _BUILTIN_COMPLEXITY[name]))

        if not matched:
            return None

        worst_name, worst_class = max(matched, key=lambda pair: pair[1].rank)
        return ComplexityEstimate(
            complexity_class=worst_class,
            rationale=(
                f"No user-written loops or recursion found, but this code calls "
                f"'{worst_name}', a standard-library function with known "
                f"{worst_class.value} complexity. This is inferred from the "
                "builtin's documented behavior, not from analyzing its internal "
                "implementation (which STRIX can't see)."
            ),
            confidence=ConfidenceLevel.MEDIUM,
        )

    @staticmethod
    def _call_name(call: ast.Call) -> str | None:
        if isinstance(call.func, ast.Name):
            return call.func.id
        if isinstance(call.func, ast.Attribute):
            return call.func.attr
        return None