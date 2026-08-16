"""
PythonComplexityEstimator: the first real (non-fake) implementation of
ComplexityEstimatorPort.

"""

import ast

from app.application.dto import CodeGraph, LoopInfo
from app.application.ports import ComplexityEstimatorPort
from app.domain.entities import ComplexityResult
from app.domain.enums import ComplexityClass, ConfidenceLevel
from app.domain.value_objects import ComplexityEstimate

_LOW_NAMES = {"low", "left", "lo", "start"}
_HIGH_NAMES = {"high", "right", "hi", "end"}
_MUTATING_METHODS = {"append", "add", "update", "extend", "insert"}


class PythonComplexityEstimator(ComplexityEstimatorPort):
    def estimate(self, graph: CodeGraph) -> ComplexityResult:
        candidates: list[tuple[ComplexityEstimate, ComplexityEstimate]] = []

        for func in graph.functions:
            if func.raw_node is None:
                continue
            recursive_calls = self._count_self_calls(func.raw_node, func.name)
            time_est = self._estimate_time(
                func.max_nesting_depth, recursive_calls, func.raw_node
            )
            space_est = self._estimate_space(recursive_calls, func.raw_node)
            candidates.append((time_est, space_est))

        if graph.top_level_loops and graph.raw_tree is not None:
            depth = self._max_depth(graph.top_level_loops)
            time_est = self._estimate_time(depth, 0, graph.raw_tree)
            space_est = self._estimate_space(0, graph.raw_tree)
            candidates.append((time_est, space_est))

        if not candidates:
            constant = ComplexityEstimate(
                complexity_class=ComplexityClass.O_1,
                rationale="No loops, recursion, or function definitions found; treated as constant-time code.",
                confidence=ConfidenceLevel.HIGH,
            )
            return ComplexityResult(
                best_case=constant, average_case=constant, worst_case=constant, space=constant
            )

        worst_time = max(candidates, key=lambda pair: pair[0].complexity_class.rank)[0]
        worst_space = max(candidates, key=lambda pair: pair[1].complexity_class.rank)[1]

        return ComplexityResult(
            best_case=worst_time,
            average_case=worst_time,
            worst_case=worst_time,
            space=worst_space,
        )

    # --- helpers -----------------------------------------------------

    @staticmethod
    def _max_depth(loops: tuple[LoopInfo, ...]) -> int:
        return max((loop.nesting_depth for loop in loops), default=0)

    @staticmethod
    def _count_self_calls(node: ast.AST, name: str) -> int:
        return sum(
            1
            for n in ast.walk(node)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name
        )

    def _estimate_time(
        self, max_depth: int, recursive_calls: int, node: ast.AST
    ) -> ComplexityEstimate:
        if recursive_calls >= 2:
            return ComplexityEstimate(
                complexity_class=ComplexityClass.O_2_N,
                rationale=(
                    f"Function calls itself {recursive_calls} times per invocation "
                    "(branching recursion, e.g. naive Fibonacci) — the call tree "
                    "grows exponentially with input size."
                ),
                confidence=ConfidenceLevel.HIGH,
            )
        if recursive_calls == 1:
            return ComplexityEstimate(
                complexity_class=ComplexityClass.O_N,
                rationale=(
                    "Function calls itself exactly once per invocation (linear "
                    "recursion) — unwinds proportionally to input size."
                ),
                confidence=ConfidenceLevel.HIGH,
            )
        if max_depth >= 3:
            return ComplexityEstimate(
                complexity_class=ComplexityClass.O_N_SQUARED,
                rationale=(
                    f"{max_depth} nested loops detected. STRIX's current complexity "
                    "scale doesn't yet distinguish polynomial degrees beyond n^2, so "
                    "this is reported as a conservative lower bound of O(n^2) rather "
                    "than a fabricated precise class."
                ),
                confidence=ConfidenceLevel.LOW,
            )
        if max_depth == 2:
            return ComplexityEstimate(
                complexity_class=ComplexityClass.O_N_SQUARED,
                rationale="Two nested loops, each iterating over the input — O(n^2) work.",
                confidence=ConfidenceLevel.HIGH,
            )
        if max_depth == 1:
            if self._has_midpoint_halving(node):
                return ComplexityEstimate(
                    complexity_class=ComplexityClass.O_LOG_N,
                    rationale=(
                        "Single loop that computes a midpoint and narrows a search "
                        "range each iteration — halving pattern indicates logarithmic growth."
                    ),
                    confidence=ConfidenceLevel.MEDIUM,
                )
            return ComplexityEstimate(
                complexity_class=ComplexityClass.O_N,
                rationale="Single loop iterating once over the input — linear time.",
                confidence=ConfidenceLevel.HIGH,
            )
        return ComplexityEstimate(
            complexity_class=ComplexityClass.O_1,
            rationale="No loops or recursion detected — constant-time operations only.",
            confidence=ConfidenceLevel.HIGH,
        )

    def _estimate_space(self, recursive_calls: int, node: ast.AST) -> ComplexityEstimate:
        if recursive_calls >= 1:
            return ComplexityEstimate(
                complexity_class=ComplexityClass.O_N,
                rationale=(
                    "Recursive calls add a frame to the call stack per level — "
                    "stack depth scales with input size."
                ),
                confidence=ConfidenceLevel.HIGH,
            )
        if self._has_growing_collection(node):
            return ComplexityEstimate(
                complexity_class=ComplexityClass.O_N,
                rationale=(
                    "Detected a collection (list/set/dict) being built up inside a "
                    "loop or comprehension — auxiliary space likely scales with input size."
                ),
                confidence=ConfidenceLevel.MEDIUM,
            )
        return ComplexityEstimate(
            complexity_class=ComplexityClass.O_1,
            rationale=(
                "No growing collections detected; auxiliary space assumed constant "
                "(heuristic — not exhaustive data-flow analysis)."
            ),
            confidence=ConfidenceLevel.MEDIUM,
        )

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

    @staticmethod
    def _has_growing_collection(node: ast.AST) -> bool:
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