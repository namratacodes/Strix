"""
BaseComplexityEstimator: the shared decision tree (recursion -> nesting
depth -> complexity class) that works for ANY language, because it
operates purely on the language-agnostic CodeGraph/FunctionInfo/LoopInfo
structures every parser produces -- never on raw AST/syntax-tree nodes
directly.

Language-specific enhancements (recognizing a midpoint-halving loop as
O(log n), recognizing a growing collection, recognizing known builtin
functions) are opt-in hooks subclasses may override. PythonComplexityEstimator
overrides all three with ast-based implementations; other languages
(GenericComplexityEstimator, used for C++/Java as of Milestone 12) get the
core decision tree only, until their own pattern recognition is added --
a deliberate, stated scope cut, not an oversight.
"""

from typing import Any

from app.application.dto import CodeGraph
from app.application.ports import ComplexityEstimatorPort
from app.domain.entities import ComplexityResult
from app.domain.enums import ComplexityClass, ConfidenceLevel
from app.domain.value_objects import ComplexityEstimate


class BaseComplexityEstimator(ComplexityEstimatorPort):
    def estimate(self, graph: CodeGraph) -> ComplexityResult:
        candidates: list[tuple[ComplexityEstimate, ComplexityEstimate]] = []

        for func in graph.functions:
            recursive_calls = func.self_call_count
            time_est = self._estimate_time(func.max_nesting_depth, recursive_calls, func.raw_node)
            space_est = self._estimate_space(recursive_calls, func.raw_node)
            candidates.append((time_est, space_est))

        if graph.top_level_loops:
            depth = max((loop.nesting_depth for loop in graph.top_level_loops), default=0)
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

    def _estimate_time(
        self, max_depth: int, recursive_calls: int, node: Any
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

        builtin_estimate = self._estimate_from_builtins(node)
        if builtin_estimate is not None:
            return builtin_estimate

        return ComplexityEstimate(
            complexity_class=ComplexityClass.O_1,
            rationale="No loops, recursion, or known complexity-bearing builtin calls detected — constant-time operations only.",
            confidence=ConfidenceLevel.HIGH,
        )

    def _estimate_space(self, recursive_calls: int, node: Any) -> ComplexityEstimate:
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
                    "Detected a collection being built up inside a loop — "
                    "auxiliary space likely scales with input size."
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

    # --- Language-specific hooks (override in subclasses) -----------------

    def _has_midpoint_halving(self, node: Any) -> bool:
        return False

    def _has_growing_collection(self, node: Any) -> bool:
        return False

    def _estimate_from_builtins(self, node: Any) -> ComplexityEstimate | None:
        return None