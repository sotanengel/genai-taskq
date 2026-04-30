from __future__ import annotations

import httpx

from genai_taskq.providers.base import ProviderResult


class AnthropicProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate(self, prompt: str, **opts: object) -> ProviderResult:
        model = str(opts.get("model", "claude-3-5-sonnet-latest"))
        payload = {
            "model": model,
            "max_tokens": int(opts.get("max_tokens", 512)),
            "messages": [{"role": "user", "content": prompt}],
        }
        with httpx.Client(timeout=30.0) as client:
            res = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
            )
            res.raise_for_status()
            data = res.json()
        text = data["content"][0]["text"]
        usage = data.get("usage", {"input_tokens": 0, "output_tokens": 0})
        return ProviderResult(
            text=text,
            model=model,
            prompt_tokens=int(usage.get("input_tokens", 0)),
            completion_tokens=int(usage.get("output_tokens", 0)),
        )
