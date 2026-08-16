from app.application.dto import CodeGraph, FunctionInfo, LoopInfo
from app.application.reasoning_timeline import ReasoningTimelineBuilder
from app.domain.entities import AlgorithmMatch, ComplexityResult
from app.domain.enums import ConfidenceLevel, Language
from app.domain.value_objects import CodeLocation, ComplexityEstimate

builder = ReasoningTimelineBuilder()


def _estimate(cls="O(n)"):
    return ComplexityEstimate(complexity_class=cls, rationale="test rationale", confidence=ConfidenceLevel.HIGH)


def test_timeline_has_eight_steps_in_order():
    graph = CodeGraph(language=Language.PYTHON, functions=(), top_level_loops=())
    complexity = ComplexityResult(
        best_case=_estimate(), average_case=_estimate(), worst_case=_estimate(), space=_estimate("O(1)")
    )
    steps = builder.build(graph, [], complexity)

    assert len(steps) == 8
    assert [s.order for s in steps] == list(range(8))
    assert steps[0].title == "Detecting language"
    assert steps[-1].title == "Generating explanation"


def test_timeline_reports_actual_loop_and_recursion_facts():
    loop = LoopInfo(location=CodeLocation(line_start=2, line_end=3), loop_type="for", nesting_depth=1)
    func = FunctionInfo(
        name="factorial",
        location=CodeLocation(line_start=1, line_end=4),
        is_recursive=True,
        loops=(),
        max_nesting_depth=0,
        calls=("factorial",),
    )
    graph = CodeGraph(language=Language.PYTHON, functions=(func,), top_level_loops=(loop,))
    complexity = ComplexityResult(
        best_case=_estimate(), average_case=_estimate(), worst_case=_estimate(), space=_estimate("O(n)")
    )

    steps = builder.build(graph, [], complexity)

    loop_step = next(s for s in steps if s.title == "Finding loops")
    assert "1 loop" in loop_step.detail

    recursion_step = next(s for s in steps if s.title == "Detecting recursion")
    assert "factorial" in recursion_step.detail


def test_timeline_reports_no_recursion_when_none_found():
    graph = CodeGraph(language=Language.PYTHON, functions=(), top_level_loops=())
    complexity = ComplexityResult(
        best_case=_estimate(), average_case=_estimate(), worst_case=_estimate(), space=_estimate("O(1)")
    )
    steps = builder.build(graph, [], complexity)
    recursion_step = next(s for s in steps if s.title == "Detecting recursion")
    assert "No recursive functions" in recursion_step.detail


def test_timeline_reports_algorithm_matches_with_confidence():
    graph = CodeGraph(language=Language.PYTHON, functions=(), top_level_loops=())
    complexity = ComplexityResult(
        best_case=_estimate(), average_case=_estimate(), worst_case=_estimate(), space=_estimate("O(1)")
    )
    match = AlgorithmMatch(name="Binary Search", confidence=ConfidenceLevel.HIGH, rationale="x")
    steps = builder.build(graph, [match], complexity)
    algo_step = next(s for s in steps if s.title == "Identifying algorithm")
    assert "Binary Search" in algo_step.detail
    assert "high confidence" in algo_step.detail


def test_timeline_reports_no_match_when_none_found():
    graph = CodeGraph(language=Language.PYTHON, functions=(), top_level_loops=())
    complexity = ComplexityResult(
        best_case=_estimate(), average_case=_estimate(), worst_case=_estimate(), space=_estimate("O(1)")
    )
    steps = builder.build(graph, [], complexity)
    algo_step = next(s for s in steps if s.title == "Identifying algorithm")
    assert "No known algorithm pattern" in algo_step.detail