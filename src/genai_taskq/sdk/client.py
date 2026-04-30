from __future__ import annotations

import httpx


class GTQClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def submit(self, prompt: str, provider: str = "mock", idempotency_key: str | None = None) -> dict:
        res = self.client.post(
            f"{self.base_url}/tasks",
            json={
                "prompt": prompt,
                "provider": provider,
                "idempotency_key": idempotency_key,
            },
        )
        res.raise_for_status()
        return res.json()

    def list(self) -> list[dict]:
        res = self.client.get(f"{self.base_url}/tasks")
        res.raise_for_status()
        return list(res.json())


class AsyncGTQClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def submit(self, prompt: str, provider: str = "mock", idempotency_key: str | None = None) -> dict:
        res = await self.client.post(
            f"{self.base_url}/tasks",
            json={
                "prompt": prompt,
                "provider": provider,
                "idempotency_key": idempotency_key,
            },
        )
        res.raise_for_status()
        return res.json()
