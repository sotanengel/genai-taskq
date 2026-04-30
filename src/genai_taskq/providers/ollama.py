from __future__ import annotations

import httpx

from genai_taskq.providers.base import ProviderResult


class OllamaProvider:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def generate(self, prompt: str, **opts: object) -> ProviderResult:
        model = str(opts.get("model", "llama3.1"))
        payload = {"model": model, "prompt": prompt, "stream": False}
        with httpx.Client(timeout=30.0) as client:
            res = client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
        text = str(data.get("response", ""))
        return ProviderResult(
            text=text,
            model=model,
        )
