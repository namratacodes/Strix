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
            
        if "Two Sum (Brute Force)" in high_confidence_names:
            suggestions.append(
                OptimizationSuggestion(
                    title="Replace brute-force Two Sum with a hash map",
                    current_approach="Nested loop checking every pair for a matching sum",
                    suggested_approach=(
                        "Single-pass hash map: store each seen value with its index; "
                        "for each new element, check if (target - element) was already seen"
                    ),
                    current_complexity="O(n^2)",
                    suggested_complexity="O(n)",
                    rationale=(
                        "Checking every pair costs O(n^2). A hash map lets you check "
                        "'have I seen the complement?' in O(1) average time per element, "
                        "so the whole search becomes a single O(n) pass — the standard "
                        "optimal solution for Two Sum."
                    ),
                    confidence=ConfidenceLevel.HIGH,
                )
            )

        if "Duplicate Check (Brute Force)" in high_confidence_names:
            suggestions.append(
                OptimizationSuggestion(
                    title="Replace brute-force duplicate check with a set",
                    current_approach="Nested loop comparing every pair of elements",
                    suggested_approach=(
                        "Single-pass set: add each element to a set while iterating; "
                        "if an element is already in the set, a duplicate/match is found"
                    ),
                    current_complexity="O(n^2)",
                    suggested_complexity="O(n)",
                    rationale=(
                        "Comparing every pair costs O(n^2). A set gives O(1) average "
                        "membership checks, so scanning once while checking 'have I "
                        "seen this before?' finds the same answer in O(n)."
                    ),
                    confidence=ConfidenceLevel.HIGH,
                )
            )

        return suggestions