from __future__ import annotations

import httpx

from genai_taskq.providers.base import ProviderResult


class LlamaCppProvider:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url

    def generate(self, prompt: str, **opts: object) -> ProviderResult:
        model = str(opts.get("model", "local-llama"))
        payload = {"prompt": prompt, "n_predict": int(opts.get("max_tokens", 256))}
        with httpx.Client(timeout=30.0) as client:
            res = client.post(
                f"{self.base_url}/completion",
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
        text = str(data.get("content", ""))
        return ProviderResult(
            text=text,
            model=model,
        )
