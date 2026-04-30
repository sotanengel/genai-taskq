from __future__ import annotations

from genai_taskq.core.models import FINAL_STATES, TaskState

ALLOWED_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.PENDING: {TaskState.SCHEDULED, TaskState.BLOCKED, TaskState.RUNNING, TaskState.CANCELED},
    TaskState.SCHEDULED: {TaskState.PENDING, TaskState.RUNNING, TaskState.CANCELED},
    TaskState.BLOCKED: {TaskState.PENDING, TaskState.CANCELED},
    TaskState.RUNNING: {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.CANCELED},
    TaskState.FAILED: {TaskState.PENDING, TaskState.CANCELED},
    TaskState.SUCCEEDED: set(),
    TaskState.CANCELED: set(),
}


def validate_transition(current: TaskState, nxt: TaskState) -> None:
    if current in FINAL_STATES:
        raise ValueError(f"cannot transition from final state: {current}")
    if nxt not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"invalid transition: {current} -> {nxt}")
