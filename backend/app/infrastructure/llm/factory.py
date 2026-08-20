"""
Factory that selects the LLMExplainerPort implementation based on config.

This is the concrete realization of "pluggable LLMs" from the PRD: the
rest of the application never imports OllamaExplainer or TemplateExplainer
directly -- it asks this factory for "the configured explainer" and gets
back something conforming to LLMExplainerPort. Swapping providers later
(e.g. adding an OpenAIExplainer) means adding one branch here, with zero
changes anywhere else in the codebase.

The configured primary is always wrapped in a ResilientExplainer, so an
unreachable/misbehaving LLM backend degrades to a deterministic
explanation instead of failing the whole analysis.
"""

from app.application.ports import LLMExplainerPort
from app.core.config import Settings
from app.infrastructure.llm.ollama_explainer import OllamaExplainer
from app.infrastructure.llm.resilient_explainer import ResilientExplainer
from app.infrastructure.llm.template_explainer import TemplateExplainer


def build_llm_explainer(settings: Settings) -> LLMExplainerPort:
    fallback = TemplateExplainer()

    if settings.llm_provider == "ollama":
        primary = OllamaExplainer(base_url=settings.ollama_base_url, model=settings.ollama_model)
        return ResilientExplainer(primary=primary, fallback=fallback)

    return fallback