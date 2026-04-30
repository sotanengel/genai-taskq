from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import and_, asc, or_, select
from sqlalchemy.exc import IntegrityError

from genai_taskq.core.models import Task, TaskState
from genai_taskq.core.state_machine import validate_transition
from genai_taskq.storage.db import SessionLocal
from genai_taskq.storage.tables import ArtifactRow, EventRow, SessionRow, TaskDependencyRow, TaskRow


def _to_task(row: TaskRow) -> Task:
    return Task(
        id=row.id,
        prompt=row.prompt,
        parent_id=row.parent_id,
        session_id=row.session_id,
        state=TaskState(row.state),
        priority=row.priority,
        run_after=row.run_after,
        lease_until=row.lease_until,
        lease_owner=row.lease_owner,
        attempts=row.attempts,
        max_retries=row.max_retries,
        backoff_base_sec=row.backoff_base_sec,
        idempotency_key=row.idempotency_key,
        provider=row.provider,
        output=row.output,
        error=row.error,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class TaskRepository:
    def create(self, task: Task) -> Task:
        with SessionLocal() as db:
            row = TaskRow(
                id=task.id,
                parent_id=task.parent_id,
                session_id=task.session_id,
                state=task.state.value,
                priority=task.priority,
                run_after=task.run_after,
                attempts=task.attempts,
                max_retries=task.max_retries,
                backoff_base_sec=task.backoff_base_sec,
                idempotency_key=task.idempotency_key,
                prompt=task.prompt,
                provider=task.provider,
            )
            db.add(row)
            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                raise ValueError("idempotency_key already exists") from exc
            db.add(EventRow(id=str(uuid4()), task_id=task.id, type="task.created"))
            db.commit()
            db.refresh(row)
            return _to_task(row)

    def get(self, task_id: str) -> Task | None:
        with SessionLocal() as db:
            row = db.get(TaskRow, task_id)
            return _to_task(row) if row else None

    def list(self) -> list[Task]:
        with SessionLocal() as db:
            rows = db.execute(select(TaskRow).order_by(TaskRow.created_at.desc())).scalars().all()
            return [_to_task(r) for r in rows]

    def add_dependency(self, task_id: str, depends_on_task_id: str) -> None:
        with SessionLocal() as db:
            db.add(TaskDependencyRow(task_id=task_id, depends_on_task_id=depends_on_task_id))
            db.commit()

    def transition(
        self, task_id: str, nxt: TaskState, error: str | None = None, output: str | None = None
    ) -> Task:
        with SessionLocal() as db:
            row = db.get(TaskRow, task_id)
            if row is None:
                raise ValueError("task not found")
            validate_transition(TaskState(row.state), nxt)
            row.state = nxt.value
            row.error = error
            row.output = output
            row.updated_at = datetime.now(UTC)
            db.commit()
            db.add(
                EventRow(
                    id=str(uuid4()), task_id=task_id, type=f"task.state.{nxt.value}", payload=error
                )
            )
            db.commit()
            db.refresh(row)
            return _to_task(row)

    def cancel(self, task_id: str) -> Task:
        return self.transition(task_id, TaskState.CANCELED)

    def dequeue(self, owner: str, lease_seconds: int = 30) -> Task | None:
        now = datetime.now(UTC)
        with SessionLocal() as db:
            rows = (
                db.execute(
                    select(TaskRow)
                    .where(
                        and_(
                            TaskRow.state.in_([TaskState.PENDING.value, TaskState.SCHEDULED.value]),
                            or_(TaskRow.run_after.is_(None), TaskRow.run_after <= now),
                            or_(TaskRow.lease_until.is_(None), TaskRow.lease_until < now),
                        )
                    )
                    .order_by(asc(TaskRow.priority), asc(TaskRow.created_at))
                    .limit(1)
                )
                .scalars()
                .all()
            )
            if not rows:
                return None
            row = rows[0]
            row.state = TaskState.RUNNING.value
            row.lease_owner = owner
            row.lease_until = now + timedelta(seconds=lease_seconds)
            row.attempts += 1
            db.commit()
            db.refresh(row)
            return _to_task(row)

    def reschedule_retry(self, task_id: str) -> Task:
        with SessionLocal() as db:
            row = db.get(TaskRow, task_id)
            if row is None:
                raise ValueError("task not found")
            task = _to_task(row)
            if not task.can_retry():
                row.state = TaskState.FAILED.value
                db.commit()
                db.refresh(row)
                return _to_task(row)
            row.state = TaskState.PENDING.value
            row.run_after = task.retry_after()
            row.lease_owner = None
            row.lease_until = None
            db.commit()
            db.refresh(row)
            return _to_task(row)

    def create_session(self, session_id: str, name: str, summary: str | None = None) -> None:
        with SessionLocal() as db:
            db.add(SessionRow(id=session_id, name=name, summary=summary))
            db.commit()

    def add_artifact(self, artifact_id: str, task_id: str, kind: str, uri: str) -> None:
        with SessionLocal() as db:
            db.add(ArtifactRow(id=artifact_id, task_id=task_id, kind=kind, uri=uri))
            db.commit()

    def list_events(self, task_id: str) -> list[dict[str, str]]:
        with SessionLocal() as db:
            rows = db.execute(select(EventRow).where(EventRow.task_id == task_id)).scalars().all()
            return [{"type": r.type, "level": r.level, "payload": r.payload or ""} for r in rows]
