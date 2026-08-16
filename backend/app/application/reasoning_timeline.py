"""
ReasoningTimelineBuilder: turns the static engine's raw findings into
STRIX's signature AI Reasoning Timeline -- a step-by-step, data-driven
narration of how the analysis reached its conclusion.

Every step here reports an actual fact pulled from the CodeGraph /
AlgorithmMatch list / ComplexityResult -- never a generic placeholder
string. This is deliberately pure narration with no LLM involved: it's
the deterministic trace that Milestone 7's LLM explainer will later
summarize in natural language, never replace.
"""

from app.application.dto import CodeGraph
from app.domain.entities import AlgorithmMatch, ComplexityResult, ReasoningStep


class ReasoningTimelineBuilder:
    def build(
        self,
        graph: CodeGraph,
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult,
    ) -> list[ReasoningStep]:
        steps: list[ReasoningStep] = []

        steps.append(
            self._step(
                len(steps),
                "Detecting language",
                f"Source identified as {graph.language.value}.",
            )
        )

        steps.append(
            self._step(
                len(steps),
                "Building code graph",
                (
                    f"Parsed source into an analysis graph with {len(graph.functions)} "
                    f"function(s) and {len(graph.top_level_loops)} top-level loop(s)."
                ),
            )
        )

        all_loops = list(graph.top_level_loops) + [
            loop for func in graph.functions for loop in func.loops
        ]
        max_depth = max((loop.nesting_depth for loop in all_loops), default=0)
        loop_detail = (
            f"Found {len(all_loops)} loop(s); deepest nesting level is {max_depth}."
            if all_loops
            else "No loops found."
        )
        steps.append(self._step(len(steps), "Finding loops", loop_detail))

        recursive_functions = [func.name for func in graph.functions if func.is_recursive]
        recursion_detail = (
            f"Recursive function(s) detected: {', '.join(recursive_functions)}."
            if recursive_functions
            else "No recursive functions detected."
        )
        steps.append(self._step(len(steps), "Detecting recursion", recursion_detail))

        if algorithm_matches:
            named = "; ".join(
                f"{m.name} ({m.confidence.value} confidence)" for m in algorithm_matches
            )
            algo_detail = f"Matched pattern(s): {named}."
        else:
            algo_detail = "No known algorithm pattern confidently matched."
        steps.append(self._step(len(steps), "Identifying algorithm", algo_detail))

        steps.append(
            self._step(
                len(steps),
                "Estimating time complexity",
                (
                    f"Worst case: {complexity.worst_case.complexity_class.value} "
                    f"({complexity.worst_case.confidence.value} confidence). "
                    f"{complexity.worst_case.rationale}"
                ),
            )
        )

        steps.append(
            self._step(
                len(steps),
                "Estimating space complexity",
                (
                    f"Auxiliary space: {complexity.space.complexity_class.value} "
                    f"({complexity.space.confidence.value} confidence). "
                    f"{complexity.space.rationale}"
                ),
            )
        )

        steps.append(
            self._step(
                len(steps),
                "Generating explanation",
                "Converting these findings into a natural-language summary.",
            )
        )

        return steps

    @staticmethod
    def _step(order: int, title: str, detail: str) -> ReasoningStep:
        return ReasoningStep(order=order, title=title, detail=detail)