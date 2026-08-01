"""
Application layer: use cases that orchestrate domain objects.

Use cases depend on abstract ports (interfaces), never on concrete
infrastructure. E.g. AnalyzeCodeUseCase depends on LanguageParserPort,
not on PythonASTParser directly.
"""
