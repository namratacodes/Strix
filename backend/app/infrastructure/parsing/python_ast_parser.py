"""
PythonASTParser: the first real (non-fake) implementation of
LanguageParserPort, using Python's built-in `ast` module.

Scope for this milestone (deliberate, stated cuts — not oversights):
- Only top-level functions are analyzed individually (class methods and
  nested functions are not yet broken out as separate FunctionInfo
  entries). This will be extended in a later pass.
- Detects loop structure (with nesting depth) and direct recursion
  (a function calling itself by name). Algorithm pattern matching
  (Binary Search, Bubble Sort, etc.) is Milestone 4's job, not this one.
"""

import ast

from app.application.dto import CodeGraph, FunctionInfo, LoopInfo
from app.application.ports import LanguageParserPort
from app.domain.enums import Language
from app.domain.value_objects import CodeLocation

_FUNCTION_SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
_LOOP_NODES = (ast.For, ast.AsyncFor, ast.While)


class PythonSyntaxError(Exception):
    """
    Raised when submitted Python source cannot be parsed.

    Kept as a domain-meaningful exception (not a raw ast.SyntaxError)
    so calling code (later, the API layer) can catch it and return a
    clean 400 response instead of leaking a stack trace.
    """


class PythonASTParser(LanguageParserPort):
    @property
    def supported_language(self) -> Language:
        return Language.PYTHON

    def parse(self, source_code: str) -> CodeGraph:
        try:
            tree = ast.parse(source_code)
        except SyntaxError as exc:
            raise PythonSyntaxError(
                f"Invalid Python syntax: {exc.msg} (line {exc.lineno})"
            ) from exc

        top_level_functions = [
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        functions = tuple(self._analyze_function(node) for node in top_level_functions)
        top_level_loops = tuple(self._find_loops(tree))

        return CodeGraph(
            language=Language.PYTHON,
            functions=functions,
            top_level_loops=top_level_loops,
            raw_tree=tree,
        )

    def _analyze_function(self, func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
        loops = tuple(self._find_loops(func_node))
        max_depth = max((loop.nesting_depth for loop in loops), default=0)

        called_names = {
            node.func.id
            for node in ast.walk(func_node)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        is_recursive = func_node.name in called_names

        return FunctionInfo(
            name=func_node.name,
            location=CodeLocation(
                line_start=func_node.lineno,
                line_end=self._end_line(func_node),
            ),
            is_recursive=is_recursive,
            loops=loops,
            max_nesting_depth=max_depth,
            calls=tuple(sorted(called_names)),
            raw_node=func_node,
        )

    def _find_loops(self, node: ast.AST, depth: int = 1) -> list[LoopInfo]:
        """
        Recursively collect loops under `node`, incrementing `depth` each
        time we descend inside a loop. Stops at nested function/lambda
        boundaries so their loops aren't attributed to the caller.

        Called with the module root -> gives top-level loops.
        Called with a single FunctionDef -> gives that function's loops
        (its own nested functions, if any, are correctly excluded).
        """
        found: list[LoopInfo] = []
        for child in ast.iter_child_nodes(node):
            if isinstance(child, _FUNCTION_SCOPE_NODES):
                continue  # nested function/lambda: analyzed separately, don't descend
            if isinstance(child, _LOOP_NODES):
                loop_type = "while" if isinstance(child, ast.While) else "for"
                found.append(
                    LoopInfo(
                        location=CodeLocation(
                            line_start=child.lineno,
                            line_end=self._end_line(child),
                        ),
                        loop_type=loop_type,
                        nesting_depth=depth,
                    )
                )
                found.extend(self._find_loops(child, depth=depth + 1))
            else:
                found.extend(self._find_loops(child, depth=depth))
        return found

    @staticmethod
    def _end_line(node: ast.AST) -> int:
        return getattr(node, "end_lineno", None) or node.lineno