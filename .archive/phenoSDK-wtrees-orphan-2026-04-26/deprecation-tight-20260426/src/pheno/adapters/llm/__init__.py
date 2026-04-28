"""
LLM adapters - implementations for language model providers.

This package contains adapter implementations for various LLM providers
(OpenAI, Anthropic, Google, etc.) that implement the LLM ports defined
in pheno.ports.llm.
"""

# Import and register adapters automatically
from ..registry import AdapterType, get_registry
from .anthropic_adapter import AnthropicAdapter
from .google_adapter import GoogleAdapter
from .openai_adapter import OpenAIAdapter

registry = get_registry()
registry.register_adapter(AdapterType.LLM, "openai", OpenAIAdapter)
registry.register_adapter(AdapterType.LLM, "anthropic", AnthropicAdapter)
registry.register_adapter(AdapterType.LLM, "google", GoogleAdapter)

__all__ = [
    "AnthropicAdapter",
    "GoogleAdapter",
    "OpenAIAdapter",
]
