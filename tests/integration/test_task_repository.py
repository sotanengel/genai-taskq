from uuid import uuid4

from genai_taskq.core.models import Task
from genai_taskq.storage.init_db import init_db
from genai_taskq.storage.repository import TaskRepository


def test_create_and_get_task() -> None:
    init_db()
    repo = TaskRepository()
    created = repo.create(Task(prompt="hello", idempotency_key=f"k-{uuid4()}"))
    got = repo.get(created.id)
    assert got is not None
    assert got.prompt == "hello"
