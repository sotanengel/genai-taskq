from __future__ import annotations

import time
from collections.abc import Callable

from genai_taskq.core.models import TaskState
from genai_taskq.providers.registry import provider_for
from genai_taskq.storage.repository import TaskRepository


class Worker:
    def __init__(self, owner: str = "worker-1", sleep_sec: float = 1.0):
        self.owner = owner
        self.sleep_sec = sleep_sec
        self.repo = TaskRepository()
        self._running = True

    def stop(self) -> None:
        self._running = False

    def loop(self, before_sleep: Callable[[], None] | None = None) -> None:
        while self._running:
            task = self.repo.dequeue(owner=self.owner)
            if task is None:
                if before_sleep:
                    before_sleep()
                time.sleep(self.sleep_sec)
                continue
            provider = provider_for(task.provider)
            try:
                result = provider.generate(task.prompt)
                self.repo.transition(task.id, TaskState.SUCCEEDED, output=result.text)
            except Exception as exc:
                _ = self.repo.transition(task.id, TaskState.FAILED, error=str(exc))
                self.repo.reschedule_retry(task.id)


def run_worker_cli() -> None:
    Worker().loop()
