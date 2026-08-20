from app.core.config import Settings
from app.infrastructure.llm.factory import build_llm_explainer
from app.infrastructure.llm.resilient_explainer import ResilientExplainer
from app.infrastructure.llm.template_explainer import TemplateExplainer


def test_ollama_provider_wraps_in_resilient_explainer():
    settings = Settings(llm_provider="ollama", ollama_base_url="http://localhost:11434", ollama_model="test-model")
    explainer = build_llm_explainer(settings)
    assert isinstance(explainer, ResilientExplainer)


def test_unknown_provider_returns_template_explainer_directly():
    settings = Settings(llm_provider="unsupported-provider")
    explainer = build_llm_explainer(settings)
    assert isinstance(explainer, TemplateExplainer)