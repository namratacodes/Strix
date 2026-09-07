"""
Factory that selects the LanguageParserPort + AlgorithmDetectorPort +
ComplexityEstimatorPort triple for a given Language. This is the single
place that knows which languages are actually supported end-to-end --
api/v1/analyze.py asks this factory rather than hardcoding an if/else
per language itself.
"""

from app.application.ports import (
    AlgorithmDetectorPort,
    ComplexityEstimatorPort,
    LanguageParserPort,
)
from app.domain.enums import Language
from app.infrastructure.complexity.generic_complexity_estimator import (
    GenericComplexityEstimator,
)
from app.infrastructure.complexity.python_complexity_estimator import (
    PythonComplexityEstimator,
)
from app.infrastructure.detection.null_algorithm_detector import NullAlgorithmDetector
from app.infrastructure.detection.tree_sitter_algorithm_detector import (
    TreeSitterAlgorithmDetector,
)
from app.infrastructure.detection.python_algorithm_detector import PythonAlgorithmDetector
from app.infrastructure.parsing.cpp_ast_parser import CppASTParser
from app.infrastructure.parsing.java_ast_parser import JavaASTParser
from app.infrastructure.parsing.python_ast_parser import PythonASTParser

_SUPPORTED_LANGUAGES: dict[
    Language,
    tuple[type[LanguageParserPort], type[AlgorithmDetectorPort], type[ComplexityEstimatorPort]],
] = {
    Language.PYTHON: (PythonASTParser, PythonAlgorithmDetector, PythonComplexityEstimator),
    Language.CPP: (CppASTParser, TreeSitterAlgorithmDetector, GenericComplexityEstimator),
    Language.JAVA: (JavaASTParser, TreeSitterAlgorithmDetector, GenericComplexityEstimator),
}


def is_language_supported(language: Language) -> bool:
    return language in _SUPPORTED_LANGUAGES


def build_parser(language: Language) -> LanguageParserPort:
    parser_cls, _, _ = _SUPPORTED_LANGUAGES[language]
    return parser_cls()


def build_algorithm_detector(language: Language) -> AlgorithmDetectorPort:
    _, detector_cls, _ = _SUPPORTED_LANGUAGES[language]
    return detector_cls()


def build_complexity_estimator(language: Language) -> ComplexityEstimatorPort:
    _, _, estimator_cls = _SUPPORTED_LANGUAGES[language]
    return estimator_cls()