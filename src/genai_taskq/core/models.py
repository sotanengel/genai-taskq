from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import uuid4


class TaskState(StrEnum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    BLOCKED = "blocked"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


FINAL_STATES = {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.CANCELED}


@dataclass(slots=True)
class Task:
    prompt: str
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str | None = None
    parent_id: str | None = None
    state: TaskState = TaskState.PENDING
    priority: int = 10
    run_after: datetime | None = None
    lease_until: datetime | None = None
    lease_owner: str | None = None
    attempts: int = 0
    max_retries: int = 3
    backoff_base_sec: int = 2
    idempotency_key: str | None = None
    provider: str = "mock"
    output: str | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def can_retry(self) -> bool:
        return self.attempts < self.max_retries

    def retry_after(self) -> datetime:
        delay = self.backoff_base_sec**max(self.attempts, 1)
        return datetime.now(UTC) + timedelta(seconds=delay)
