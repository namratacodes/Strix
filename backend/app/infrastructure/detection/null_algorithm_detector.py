"""
NullAlgorithmDetector: returns no matches, always. Used for languages
that have parsing + complexity estimation (Milestone 12) but not yet
their own algorithm pattern detection (C++, Java) -- keeps the pipeline
honest ("no known pattern matched") rather than pretending Python's
ast-based PythonAlgorithmDetector patterns apply to other languages'
syntax trees, which they don't.
"""

from app.application.dto import CodeGraph
from app.application.ports import AlgorithmDetectorPort
from app.domain.entities import AlgorithmMatch


class NullAlgorithmDetector(AlgorithmDetectorPort):
    def detect(self, graph: CodeGraph) -> list[AlgorithmMatch]:
        return []