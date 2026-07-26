from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from backend.app.error import InvalidTaskError
from backend.app.models.enums import TaskStatus
from backend.app.models.task import Task
from backend.app.schemas.task import TaskMove
from backend.app.services import tasks as tasks_service_module
from backend.app.services.tasks import TaskService


MOVED_AT = datetime(2026, 7, 26, 12, 30, tzinfo=timezone.utc)
STARTED_AT = datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc)
REVIEWED_AT = datetime(2026, 7, 24, 10, 0, tzinfo=timezone.utc)
COMPLETED_AT = datetime(2026, 7, 25, 11, 0, tzinfo=timezone.utc)


def make_task(status: TaskStatus, **overrides: object) -> Task:
    values = {
        "id": 10,
        "team_id": 20,
        "creator_member_id": 30,
        "reviewer_member_id": 40,
        "title": "Move me",
        "status": status,
        "position": 2000,
        "should_review": True,
        "started_working_at": STARTED_AT,
        "submitted_for_review_at": REVIEWED_AT,
        "completed_at": COMPLETED_AT,
        "returned_count": 2,
        "reopened_count": 3,
        "blocked_count": 4,
    }
    values.update(overrides)
    return Task(**values)


def arrange_move(monkeypatch: pytest.MonkeyPatch, neighbors=(None, None)) -> tuple[TaskService, Mock]:
    db = Mock()
    monkeypatch.setattr(tasks_service_module, "lock_task_positions", Mock())
    monkeypatch.setattr(tasks_service_module, "get_destination_neighbors", Mock(return_value=neighbors))
    monkeypatch.setattr(tasks_service_module, "datetime", Mock(now=Mock(return_value=MOVED_AT)))
    service = TaskService()
    monkeypatch.setattr(service, "_can_create_in_progress_task", Mock(return_value=True))
    return service, db


@pytest.mark.parametrize("_scenario", [None], ids=["SVC-001"])
def test_review_reentry_to_active_work(monkeypatch: pytest.MonkeyPatch, _scenario: None) -> None:
    service, db = arrange_move(monkeypatch)
    task = make_task(TaskStatus.REVIEW)

    result = service.move_task(db, task, TaskMove(target_status=TaskStatus.IN_PROGRESS))

    assert result is task
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.returned_count == 3
    assert task.started_working_at == MOVED_AT
    assert task.submitted_for_review_at is None
    assert task.completed_at is None


@pytest.mark.parametrize("target", [TaskStatus.TODO, TaskStatus.BACKLOG], ids=["TODO", "BACKLOG"])
@pytest.mark.parametrize("_scenario", [None], ids=["SVC-002"])
def test_review_return_before_work(
    monkeypatch: pytest.MonkeyPatch, _scenario: None, target: TaskStatus
) -> None:
    service, db = arrange_move(monkeypatch)
    task = make_task(TaskStatus.REVIEW)

    service.move_task(db, task, TaskMove(target_status=target))

    assert task.returned_count == 3
    assert task.started_working_at is None
    assert task.submitted_for_review_at is None
    assert task.completed_at is None


@pytest.mark.parametrize("_scenario", [None], ids=["SVC-003"])
def test_done_reentry_to_review(monkeypatch: pytest.MonkeyPatch, _scenario: None) -> None:
    service, db = arrange_move(monkeypatch)
    task = make_task(TaskStatus.DONE)

    service.move_task(db, task, TaskMove(target_status=TaskStatus.REVIEW))

    assert task.reopened_count == 4
    assert task.started_working_at == STARTED_AT
    assert task.submitted_for_review_at == MOVED_AT
    assert task.completed_at is None


@pytest.mark.parametrize("_scenario", [None], ids=["SVC-004"])
def test_done_reentry_to_active_work(monkeypatch: pytest.MonkeyPatch, _scenario: None) -> None:
    service, db = arrange_move(monkeypatch)
    task = make_task(TaskStatus.DONE)

    service.move_task(db, task, TaskMove(target_status=TaskStatus.IN_PROGRESS))

    assert task.reopened_count == 4
    assert task.started_working_at == MOVED_AT
    assert task.submitted_for_review_at is None
    assert task.completed_at is None


@pytest.mark.parametrize("target", [TaskStatus.TODO, TaskStatus.BACKLOG], ids=["TODO", "BACKLOG"])
@pytest.mark.parametrize("_scenario", [None], ids=["SVC-005"])
def test_done_return_before_work(
    monkeypatch: pytest.MonkeyPatch, _scenario: None, target: TaskStatus
) -> None:
    service, db = arrange_move(monkeypatch)
    task = make_task(TaskStatus.DONE)

    service.move_task(db, task, TaskMove(target_status=target))

    assert task.reopened_count == 4
    assert task.started_working_at is None
    assert task.submitted_for_review_at is None
    assert task.completed_at is None


@pytest.mark.parametrize(
    ("source", "target", "neighbors"),
    [
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS, (None, None)),
        (TaskStatus.TODO, TaskStatus.TODO, (None, make_task(TaskStatus.TODO, id=11, position=1000))),
    ],
    ids=["forward-transition", "same-status-reorder"],
)
@pytest.mark.parametrize("_scenario", [None], ids=["SVC-006"])
def test_movement_keeps_event_counters_stable(
    monkeypatch: pytest.MonkeyPatch,
    _scenario: None,
    source: TaskStatus,
    target: TaskStatus,
    neighbors: tuple[Task | None, Task | None],
) -> None:
    service, db = arrange_move(monkeypatch, neighbors)
    task = make_task(source)

    service.move_task(db, task, TaskMove(target_status=target))

    assert (task.returned_count, task.reopened_count, task.blocked_count) == (2, 3, 4)


@pytest.mark.parametrize("_scenario", [None], ids=["SVC-007"])
def test_non_reviewable_task_cannot_enter_review(
    monkeypatch: pytest.MonkeyPatch, _scenario: None
) -> None:
    service, db = arrange_move(monkeypatch)
    task = make_task(TaskStatus.IN_PROGRESS, should_review=False, reviewer_member_id=None)

    with pytest.raises(InvalidTaskError):
        service.move_task(db, task, TaskMove(target_status=TaskStatus.REVIEW))


@pytest.mark.parametrize("_scenario", [None], ids=["SVC-008"])
def test_self_anchor_returns_refreshed_task_without_mutation(
    monkeypatch: pytest.MonkeyPatch, _scenario: None
) -> None:
    calls: list[str] = []
    db = Mock()
    db.refresh.side_effect = lambda task: calls.append("refresh")
    lock = Mock(side_effect=lambda db, team_id: calls.append("lock"))
    mutation = Mock()
    rebalance = Mock()
    neighbors = Mock()
    capacity = Mock()
    validation = Mock()
    monkeypatch.setattr(tasks_service_module, "lock_task_positions", lock)
    monkeypatch.setattr(tasks_service_module, "update_task_repository", mutation)
    monkeypatch.setattr(tasks_service_module, "rebalance_task_column", rebalance)
    monkeypatch.setattr(tasks_service_module, "get_destination_neighbors", neighbors)
    monkeypatch.setattr(TaskService, "_can_create_in_progress_task", capacity)
    monkeypatch.setattr(TaskService, "_validate_move", validation)
    task = make_task(TaskStatus.TODO)

    result = TaskService().move_task(
        db,
        task,
        TaskMove(target_status=TaskStatus.DONE, anchor_task_id=task.id),
    )

    assert result is task
    assert calls == ["lock", "refresh"]
    neighbors.assert_not_called()
    capacity.assert_not_called()
    validation.assert_not_called()
    mutation.assert_not_called()
    rebalance.assert_not_called()


@pytest.mark.parametrize("_scenario", [None], ids=["SVC-009"])
def test_matching_current_adjacency_is_a_placement_noop(
    monkeypatch: pytest.MonkeyPatch, _scenario: None
) -> None:
    anchor = make_task(TaskStatus.TODO, id=9, position=1000)
    successor = make_task(TaskStatus.TODO, id=11, position=3000)
    service, db = arrange_move(monkeypatch, (anchor, successor))
    mutation = Mock()
    rebalance = Mock()
    monkeypatch.setattr(tasks_service_module, "update_task_repository", mutation)
    monkeypatch.setattr(tasks_service_module, "rebalance_task_column", rebalance)
    task = make_task(TaskStatus.TODO)

    result = service.move_task(
        db, task, TaskMove(target_status=TaskStatus.TODO, anchor_task_id=anchor.id)
    )

    assert result is task
    mutation.assert_not_called()
    rebalance.assert_not_called()


@pytest.mark.parametrize(
    ("case", "payload", "neighbors"),
    [
        ("invalid-forward", TaskMove(target_status=TaskStatus.DONE), (None, None)),
        ("missing-anchor", TaskMove(target_status=TaskStatus.TODO, anchor_task_id=91), (None, None)),
        ("wrong-team-anchor", TaskMove(target_status=TaskStatus.TODO, anchor_task_id=92), (None, None)),
        ("wrong-status-anchor", TaskMove(target_status=TaskStatus.TODO, anchor_task_id=93), (None, None)),
    ],
    ids=["invalid-forward", "missing-anchor", "wrong-team-anchor", "wrong-status-anchor"],
)
@pytest.mark.parametrize("_scenario", [None], ids=["SVC-010"])
def test_invalid_client_movement_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    _scenario: None,
    case: str,
    payload: TaskMove,
    neighbors: tuple[Task | None, Task | None],
) -> None:
    del case
    service, db = arrange_move(monkeypatch, neighbors)
    task = make_task(TaskStatus.BACKLOG)

    with pytest.raises(InvalidTaskError):
        service.move_task(db, task, payload)


@pytest.mark.parametrize("_scenario", [None], ids=["SVC-011"])
def test_same_status_active_reorder_does_not_read_capacity(
    monkeypatch: pytest.MonkeyPatch, _scenario: None
) -> None:
    successor = make_task(TaskStatus.IN_PROGRESS, id=11, position=1000)
    service, db = arrange_move(monkeypatch, (None, successor))
    capacity = Mock()
    monkeypatch.setattr(service, "_can_create_in_progress_task", capacity)
    task = make_task(TaskStatus.IN_PROGRESS)

    service.move_task(db, task, TaskMove(target_status=TaskStatus.IN_PROGRESS))

    capacity.assert_not_called()
    assert task.position == 500
