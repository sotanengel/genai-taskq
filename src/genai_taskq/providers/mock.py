from __future__ import annotations

from genai_taskq.providers.base import ProviderResult


class MockProvider:
    def generate(self, prompt: str, **opts: object) -> ProviderResult:
        return ProviderResult(text=f"mock:{prompt}", model="mock")
