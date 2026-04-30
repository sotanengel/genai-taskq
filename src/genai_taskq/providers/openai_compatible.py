from __future__ import annotations

import os

import httpx

from genai_taskq.providers.base import ProviderResult


class OpenAICompatibleProvider:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    def generate(self, prompt: str, **opts: object) -> ProviderResult:
        model = str(opts.get("model", "gpt-4o-mini"))
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        with httpx.Client(timeout=30.0) as client:
            res = client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return ProviderResult(
            text=text,
            model=model,
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
        )
