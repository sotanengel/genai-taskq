from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from genai_taskq.api.schemas import TaskCreateRequest, TaskResponse
from genai_taskq.core.models import Task, TaskState
from genai_taskq.mcp.server import router as mcp_router
from genai_taskq.observability.metrics import submit_counter
from genai_taskq.storage.init_db import init_db
from genai_taskq.storage.repository import TaskRepository

app = FastAPI(title="genai-taskq", version="0.1.0")
app.include_router(mcp_router)
repo = TaskRepository()
init_db()


def _to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        state=task.state.value,
        prompt=task.prompt,
        provider=task.provider,
        output=task.output,
        error=task.error,
        attempts=task.attempts,
    )


@app.post("/tasks", response_model=TaskResponse)
def submit_task(req: TaskCreateRequest) -> TaskResponse:
    state = TaskState.SCHEDULED if req.run_after else TaskState.PENDING
    task = Task(
        prompt=req.prompt,
        provider=req.provider,
        priority=req.priority,
        idempotency_key=req.idempotency_key,
        run_after=req.run_after,
        max_retries=req.max_retries,
        backoff_base_sec=req.backoff_base_sec,
        state=state,
    )
    created = repo.create(task)
    for dep in req.depends_on:
        repo.add_dependency(created.id, dep)
    submit_counter.inc()
    return _to_response(created)


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks() -> list[TaskResponse]:
    return [_to_response(t) for t in repo.list()]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str) -> TaskResponse:
    task = repo.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return _to_response(task)


@app.post("/tasks/{task_id}/cancel", response_model=TaskResponse)
def cancel_task(task_id: str) -> TaskResponse:
    return _to_response(repo.cancel(task_id))


@app.get("/tasks/{task_id}/logs")
def task_logs(task_id: str) -> list[dict[str, str]]:
    return repo.list_events(task_id)


@app.post("/sessions")
def create_session(name: str, summary: str | None = None) -> dict[str, str]:
    sid = str(uuid4())
    repo.create_session(sid, name=name, summary=summary)
    return {"id": sid}


@app.post("/tasks/{task_id}/artifacts")
def add_artifact(task_id: str, kind: str, uri: str) -> dict[str, str]:
    aid = str(uuid4())
    repo.add_artifact(aid, task_id=task_id, kind=kind, uri=uri)
    return {"id": aid}


@app.get("/sse/tasks")
def sse_tasks() -> StreamingResponse:
    payload = "event: ping\ndata: task stream placeholder\n\n"
    return StreamingResponse(iter([payload]), media_type="text/event-stream")


@app.get("/metrics")
def metrics() -> StreamingResponse:
    return StreamingResponse(iter([generate_latest()]), media_type=CONTENT_TYPE_LATEST)
