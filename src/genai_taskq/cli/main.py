from __future__ import annotations

import typer

from genai_taskq.core.models import Task
from genai_taskq.storage.init_db import init_db
from genai_taskq.storage.repository import TaskRepository

app = typer.Typer(help="genai-taskq CLI")
repo = TaskRepository()


@app.command("init")
def init_cmd() -> None:
    init_db()
    typer.echo("initialized")


@app.command("submit")
def submit_cmd(prompt: str, provider: str = "mock", idempotency_key: str | None = None) -> None:
    task = repo.create(Task(prompt=prompt, provider=provider, idempotency_key=idempotency_key))
    typer.echo(task.id)


@app.command("list")
def list_cmd() -> None:
    for task in repo.list():
        typer.echo(f"{task.id}\t{task.state.value}\t{task.prompt}")


@app.command("show")
def show_cmd(task_id: str) -> None:
    task = repo.get(task_id)
    if task is None:
        raise typer.Exit(code=1)
    typer.echo(f"{task.id}\nstate={task.state.value}\noutput={task.output}\nerror={task.error}")


@app.command("cancel")
def cancel_cmd(task_id: str) -> None:
    task = repo.cancel(task_id)
    typer.echo(f"{task.id}\t{task.state.value}")


@app.command("logs")
def logs_cmd(task_id: str) -> None:
    task = repo.get(task_id)
    if task is None:
        raise typer.Exit(code=1)
    typer.echo(task.output or task.error or "(no logs)")
