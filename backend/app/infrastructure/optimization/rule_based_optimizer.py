from app.application.ports import OptimizerPort
from app.domain.entities import AlgorithmMatch, ComplexityResult, OptimizationSuggestion
from app.domain.enums import ConfidenceLevel


class RuleBasedOptimizer(OptimizerPort):
    def suggest(
        self,
        algorithm_matches: list[AlgorithmMatch],
        complexity: ComplexityResult | None,
    ) -> list[OptimizationSuggestion]:
        high_confidence_names = {
            m.name for m in algorithm_matches if m.confidence == ConfidenceLevel.HIGH
        }
        suggestions: list[OptimizationSuggestion] = []

        if "Bubble Sort" in high_confidence_names:
            suggestions.append(
                OptimizationSuggestion(
                    title="Replace Bubble Sort with a built-in sort",
                    current_approach="Bubble Sort — repeatedly comparing and swapping adjacent elements",
                    suggested_approach="The language's built-in sort (e.g. Python's sorted()/list.sort(), which uses Timsort)",
                    current_complexity="O(n^2)",
                    suggested_complexity="O(n log n)",
                    rationale=(
                        "Bubble Sort does O(n^2) comparisons and swaps even in typical cases. "
                        "Built-in sorts use well-tested O(n log n) algorithms (e.g. Timsort) "
                        "implemented in optimized native code — meaningfully faster for any "
                        "list beyond a handful of elements. Bubble Sort is only worth keeping "
                        "for teaching purposes or genuinely tiny, nearly-sorted inputs."
                    ),
                    confidence=ConfidenceLevel.HIGH,
                )
            )

        return suggestions