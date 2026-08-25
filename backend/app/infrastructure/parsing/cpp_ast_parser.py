"""
CppASTParser: the first Tree-sitter-backed LanguageParserPort implementation.

Mirrors PythonASTParser's structure closely on purpose: same recursive
loop-finding strategy (stop at nested function boundaries), same
self-call counting, same CodeGraph/FunctionInfo/LoopInfo output shape.
This is what lets BaseComplexityEstimator (Milestone 12's refactor) work
identically for C++ as it already does for Python -- the estimator never
needs to know which language it's looking at.

Scope for this milestone (deliberate, stated cuts):
- Only free functions are analyzed (not class methods) -- same
  intentional limitation as Python's parser in Milestone 3.
- Algorithm pattern detection (Bubble Sort, Binary Search, etc.) for C++
  is NOT included in this pass -- PythonAlgorithmDetector's ast-based
  pattern matching doesn't transfer to Tree-sitter nodes; a
  CppAlgorithmDetector is a separate, later piece of work.
"""

import tree_sitter_cpp
from tree_sitter import Language, Node, Parser

from app.application.dto import CodeGraph, FunctionInfo, LoopInfo
from app.application.ports import LanguageParserPort
from app.domain.enums import Language as STRIXLanguage
from app.domain.value_objects import CodeLocation

_CPP_LANGUAGE = Language(tree_sitter_cpp.language())

_FUNCTION_NODES = {"function_definition"}
_LOOP_NODES = {"for_statement", "while_statement", "do_statement"}


class CppSyntaxError(Exception):
    """Raised when submitted C++ source cannot be parsed."""


class CppASTParser(LanguageParserPort):
    def __init__(self) -> None:
        self._parser = Parser(_CPP_LANGUAGE)

    @property
    def supported_language(self) -> STRIXLanguage:
        return STRIXLanguage.CPP

    def parse(self, source_code: str) -> CodeGraph:
        source_bytes = source_code.encode("utf-8")
        tree = self._parser.parse(source_bytes)

        if tree.root_node.has_error:
            raise CppSyntaxError("Invalid C++ syntax detected by the parser.")

        top_level_functions = [
            node for node in tree.root_node.children if node.type == "function_definition"
        ]
        functions = tuple(
            self._analyze_function(node, source_bytes) for node in top_level_functions
        )
        top_level_loops = tuple(self._find_loops(tree.root_node, source_bytes))

        return CodeGraph(
            language=STRIXLanguage.CPP,
            functions=functions,
            top_level_loops=top_level_loops,
            raw_tree=tree,
        )

    def _analyze_function(self, func_node: Node, source_bytes: bytes) -> FunctionInfo:
        name = self._function_name(func_node) or "<anonymous>"
        loops = tuple(self._find_loops(func_node, source_bytes))
        max_depth = max((loop.nesting_depth for loop in loops), default=0)

        call_names = self._find_call_names(func_node)
        self_call_count = call_names.count(name)
        is_recursive = self_call_count > 0

        return FunctionInfo(
            name=name,
            location=CodeLocation(
                line_start=func_node.start_point[0] + 1,
                line_end=func_node.end_point[0] + 1,
            ),
            is_recursive=is_recursive,
            loops=loops,
            max_nesting_depth=max_depth,
            calls=tuple(sorted(set(call_names))),
            self_call_count=self_call_count,
            raw_node=func_node,
        )

    def _find_loops(self, node: Node, source_bytes: bytes, depth: int = 1) -> list[LoopInfo]:
        found: list[LoopInfo] = []
        for child in node.children:
            if child.type in _FUNCTION_NODES and child is not node:
                continue
            if child.type in _LOOP_NODES:
                found.append(
                    LoopInfo(
                        location=CodeLocation(
                            line_start=child.start_point[0] + 1,
                            line_end=child.end_point[0] + 1,
                        ),
                        loop_type="while" if "while" in child.type else "for",
                        nesting_depth=depth,
                    )
                )
                found.extend(self._find_loops(child, source_bytes, depth=depth + 1))
            else:
                found.extend(self._find_loops(child, source_bytes, depth=depth))
        return found

    def _find_call_names(self, node: Node) -> list[str]:
        names: list[str] = []
        for child in node.children:
            if child.type == "call_expression" and child.children:
                callee = child.children[0]
                if callee.type == "identifier":
                    names.append(callee.text.decode("utf-8"))
            names.extend(self._find_call_names(child))
        return names

    @staticmethod
    def _function_name(func_node: Node) -> str | None:
        declarator = func_node.child_by_field_name("declarator")
        if declarator is None:
            return None
        current = declarator
        while current is not None:
            if current.type == "identifier":
                return current.text.decode("utf-8")
            inner = current.child_by_field_name("declarator")
            if inner is None:
                break
            current = inner
        return None