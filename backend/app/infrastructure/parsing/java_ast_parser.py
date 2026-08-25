"""
JavaASTParser: second Tree-sitter-backed LanguageParserPort implementation.

Key structural difference from Python/C++: Java has no free-standing
functions -- every method lives inside a class. So "top-level function"
for this parser means "method_declaration found anywhere in the file"
rather than "function defined at module scope". This is a deliberate
adaptation, not an inconsistency: it's the natural Java equivalent of
what Python/C++'s top-level functions represent.

Scope for this milestone (same stated cuts as CppASTParser):
- Only ordinary methods are analyzed; constructors and nested/inner
  classes are not specially handled yet.
- No algorithm pattern detection for Java in this pass.
"""

import tree_sitter_java
from tree_sitter import Language, Node, Parser

from app.application.dto import CodeGraph, FunctionInfo, LoopInfo
from app.application.ports import LanguageParserPort
from app.domain.enums import Language as STRIXLanguage
from app.domain.value_objects import CodeLocation

_JAVA_LANGUAGE = Language(tree_sitter_java.language())

_FUNCTION_NODES = {"method_declaration", "constructor_declaration"}
_LOOP_NODES = {"for_statement", "while_statement", "do_statement", "enhanced_for_statement"}


class JavaSyntaxError(Exception):
    """Raised when submitted Java source cannot be parsed."""


class JavaASTParser(LanguageParserPort):
    def __init__(self) -> None:
        self._parser = Parser(_JAVA_LANGUAGE)

    @property
    def supported_language(self) -> STRIXLanguage:
        return STRIXLanguage.JAVA

    def parse(self, source_code: str) -> CodeGraph:
        source_bytes = source_code.encode("utf-8")
        tree = self._parser.parse(source_bytes)

        if tree.root_node.has_error:
            raise JavaSyntaxError("Invalid Java syntax detected by the parser.")

        method_nodes = list(self._find_methods(tree.root_node))
        functions = tuple(self._analyze_function(node) for node in method_nodes)

        return CodeGraph(
            language=STRIXLanguage.JAVA,
            functions=functions,
            top_level_loops=(),
            raw_tree=tree,
        )

    def _find_methods(self, node: Node):
        for child in node.children:
            if child.type in _FUNCTION_NODES:
                yield child
            yield from self._find_methods(child)

    def _analyze_function(self, func_node: Node) -> FunctionInfo:
        name_node = func_node.child_by_field_name("name")
        name = name_node.text.decode("utf-8") if name_node else "<anonymous>"

        loops = tuple(self._find_loops(func_node))
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

    def _find_loops(self, node: Node, depth: int = 1) -> list[LoopInfo]:
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
                found.extend(self._find_loops(child, depth=depth + 1))
            else:
                found.extend(self._find_loops(child, depth=depth))
        return found

    def _find_call_names(self, node: Node) -> list[str]:
        names: list[str] = []
        for child in node.children:
            if child.type == "method_invocation":
                name_node = child.child_by_field_name("name")
                if name_node is not None:
                    names.append(name_node.text.decode("utf-8"))
            names.extend(self._find_call_names(child))
        return names