"""
GenericComplexityEstimator: used for languages that have Tree-sitter
parsing but not yet their own complexity-pattern recognition (C++, Java
as of Milestone 12). Provides the full core decision tree (recursion,
nesting depth) with no overrides -- O(log n) midpoint detection, growing-
collection detection, and builtin recognition are not yet implemented for
these languages. This is a deliberate, stated scope cut: extending these
per-language is planned future work, not an oversight.
"""

from app.infrastructure.complexity.base_complexity_estimator import BaseComplexityEstimator


class GenericComplexityEstimator(BaseComplexityEstimator):
    pass