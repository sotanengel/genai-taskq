import pytest

from genai_taskq.core.models import TaskState
from genai_taskq.core.state_machine import validate_transition


def test_valid_transition_pending_to_running() -> None:
    validate_transition(TaskState.PENDING, TaskState.RUNNING)


def test_invalid_transition_from_succeeded() -> None:
    with pytest.raises(ValueError):
        validate_transition(TaskState.SUCCEEDED, TaskState.PENDING)
