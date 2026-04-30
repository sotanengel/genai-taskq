from __future__ import annotations

from fastapi import APIRouter

from genai_taskq.core.models import Task
from genai_taskq.storage.repository import TaskRepository

router = APIRouter(prefix="/mcp", tags=["mcp"])
repo = TaskRepository()


@router.post("/submit")
def mcp_submit(prompt: str) -> dict[str, str]:
    task = repo.create(Task(prompt=prompt))
    return {"task_id": task.id}


@router.get("/task/{task_id}")
def mcp_get(task_id: str) -> dict[str, str]:
    task = repo.get(task_id)
    if task is None:
        return {"status": "not_found"}
    return {"task_id": task.id, "state": task.state.value}


@router.post("/cancel/{task_id}")
def mcp_cancel(task_id: str) -> dict[str, str]:
    task = repo.cancel(task_id)
    return {"task_id": task.id, "state": task.state.value}
