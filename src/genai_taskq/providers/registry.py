from __future__ import annotations

import os

from genai_taskq.providers.anthropic import AnthropicProvider
from genai_taskq.providers.base import Provider
from genai_taskq.providers.llama_cpp import LlamaCppProvider
from genai_taskq.providers.mock import MockProvider
from genai_taskq.providers.ollama import OllamaProvider
from genai_taskq.providers.openai_compatible import OpenAICompatibleProvider


def provider_for(name: str) -> Provider:
    if name == "openai":
        return OpenAICompatibleProvider()
    if name == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY", "")
        return AnthropicProvider(api_key=key)
    if name == "ollama":
        return OllamaProvider()
    if name == "llama_cpp":
        return LlamaCppProvider()
    return MockProvider()
