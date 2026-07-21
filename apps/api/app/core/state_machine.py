"""Centralized Job State Machine.

Defines all legal job-state transitions and validates them.
Every component that changes job status must use this module.
"""

from typing import Dict, Set, Optional

# Canonical job states (from Technical Specification)
JOB_STATUS_PENDING = "pending"
JOB_STATUS_QUEUED = "queued"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_PAUSED = "paused"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"
JOB_STATUS_RETRYING = "retrying"
JOB_STATUS_CANCELLED = "cancelled"

ALL_JOB_STATUSES = {
    JOB_STATUS_PENDING, JOB_STATUS_QUEUED, JOB_STATUS_RUNNING,
    JOB_STATUS_PAUSED, JOB_STATUS_COMPLETED, JOB_STATUS_FAILED,
    JOB_STATUS_RETRYING, JOB_STATUS_CANCELLED,
}

# Legal transitions: {from_state: {to_state1, to_state2, ...}}
TRANSITIONS: Dict[str, Set[str]] = {
    JOB_STATUS_PENDING: {JOB_STATUS_QUEUED, JOB_STATUS_CANCELLED},
    JOB_STATUS_QUEUED: {JOB_STATUS_RUNNING, JOB_STATUS_CANCELLED},
    JOB_STATUS_RUNNING: {JOB_STATUS_PAUSED, JOB_STATUS_COMPLETED, JOB_STATUS_FAILED, JOB_STATUS_CANCELLED},
    JOB_STATUS_PAUSED: {JOB_STATUS_QUEUED, JOB_STATUS_CANCELLED},
    JOB_STATUS_COMPLETED: set(),  # Terminal state
    JOB_STATUS_FAILED: {JOB_STATUS_RETRYING},
    JOB_STATUS_RETRYING: {JOB_STATUS_QUEUED},
    JOB_STATUS_CANCELLED: set(),  # Terminal state
}


def is_valid_transition(from_status: str, to_status: str) -> bool:
    """Check if a transition from from_status to to_status is permitted."""
    if from_status not in TRANSITIONS:
        return False
    return to_status in TRANSITIONS[from_status]


def is_terminal(status: str) -> bool:
    """Check if a status is terminal (no further transitions allowed)."""
    if status not in TRANSITIONS:
        return False
    return len(TRANSITIONS[status]) == 0


def get_permitted_transitions(from_status: str) -> Set[str]:
    """Return the set of legal target states from the given status."""
    return TRANSITIONS.get(from_status, set())


class InvalidTransitionError(ValueError):
    """Raised when an illegal job-state transition is attempted."""

    def __init__(self, from_status: str, to_status: str):
        self.from_status = from_status
        self.to_status = to_status
        permitted = get_permitted_transitions(from_status)
        msg = f"Cannot transition job from '{from_status}' to '{to_status}'. Permitted: {permitted or '(terminal state)'}"
        super().__init__(msg)