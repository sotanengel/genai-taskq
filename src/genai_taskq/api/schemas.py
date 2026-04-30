from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    prompt: str
    provider: str = "mock"
    priority: int = 10
    idempotency_key: str | None = None
    run_after: datetime | None = None
    max_retries: int = 3
    backoff_base_sec: int = 2
    depends_on: list[str] = Field(default_factory=list)


class TaskResponse(BaseModel):
    id: str
    state: str
    prompt: str
    provider: str
    output: str | None
    error: str | None
    attempts: int
