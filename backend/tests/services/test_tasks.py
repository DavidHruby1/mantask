from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from sqlalchemy.orm import Session

from backend.app.error import (
    ApiConflictError,
    ApiInternalServerError,
    InvalidTaskError,
    NoActiveTeamSelectedError,
    TaskAccessDeniedError,
    TaskNotFoundError,
    TeamInactiveError,
    TeamMembershipError,
    TeamNotFoundError,
)
from backend.app.models.enums import TaskStatus
from backend.app.schemas.task import (
    TaskCreate,
    TaskFilters,
    TaskMove,
    TaskQuery,
    TaskUpdate,
)
from backend.app.services import tasks as tasks_service
from backend.app.services.tasks import TaskService


_STARTED_AT = datetime(2026, 7, 20, 9, 0, tzinfo=timezone.utc)
_REVIEWED_AT = datetime(2026, 7, 21, 9, 0, tzinfo=timezone.utc)
_COMPLETED_AT = datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc)
_MOVED_AT = datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc)


def _task_for_move(status: TaskStatus, **overrides):
    values = {
        "id": 1,
        "team_id": 20,
        "status": status,
        "position": 5000,
        "should_review": True,
        "started_working_at": _STARTED_AT,
        "submitted_for_review_at": _REVIEWED_AT,
        "completed_at": _COMPLETED_AT,
        "returned_count": 2,
        "reopened_count": 3,
        "blocked_count": 4,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_get_all_tasks_uses_explicit_team_and_filters(monkeypatch):
    db = Mock(spec=Session)
    session = SimpleNamespace(user_id=10)
    query = TaskQuery(
        team_id=20,
        statuses=[TaskStatus.TODO],
        assignee_member_id=30,
    )
    tasks = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    find_tasks = Mock(return_value=tasks)
    get_team = Mock(return_value=SimpleNamespace(is_active=True))
    is_member = Mock(return_value=True)
    get_assignee = Mock(return_value=SimpleNamespace(id=30))
    monkeypatch.setattr(tasks_service, "get_team_by_id", get_team)
    monkeypatch.setattr(tasks_service, "is_team_member", is_member)
    monkeypatch.setattr(tasks_service, "get_team_member_by_id", get_assignee)
    monkeypatch.setattr(tasks_service, "find_tasks", find_tasks)

    result = TaskService().get_all_tasks(db, session, query)

    find_tasks.assert_called_once_with(
        db,
        TaskFilters(
            team_id=20,
            statuses=[TaskStatus.TODO],
            assignee_member_id=30,
        ),
    )
    get_team.assert_called_once_with(db, 20)
    is_member.assert_called_once_with(db, 20, 10)
    get_assignee.assert_called_once_with(db, 20, 30)
    assert result is tasks


def test_get_all_tasks_uses_last_active_team(monkeypatch):
    db = Mock(spec=Session)
    session = SimpleNamespace(
        user_id=10,
        user=SimpleNamespace(last_active_team_id=20),
    )
    find_tasks = Mock(return_value=[])
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=SimpleNamespace(is_active=True)),
    )
    monkeypatch.setattr(tasks_service, "is_team_member", Mock(return_value=True))
    monkeypatch.setattr(tasks_service, "find_tasks", find_tasks)

    result = TaskService().get_all_tasks(db, session, TaskQuery())

    find_tasks.assert_called_once_with(
        db,
        TaskFilters(team_id=20, statuses=[], assignee_member_id=None),
    )
    assert result == []


def test_get_all_tasks_requires_active_team_selection():
    db = Mock(spec=Session)
    session = SimpleNamespace(
        user_id=10,
        user=SimpleNamespace(last_active_team_id=None),
    )

    with pytest.raises(NoActiveTeamSelectedError):
        TaskService().get_all_tasks(db, session, TaskQuery())


@pytest.mark.parametrize(
    ("team", "is_member"),
    [
        (None, True),
        (SimpleNamespace(is_active=False), True),
        (SimpleNamespace(is_active=True), False),
    ],
    ids=["missing-team", "inactive-team", "not-a-member"],
)
def test_get_all_tasks_denies_inaccessible_team(
    monkeypatch,
    team,
    is_member,
):
    db = Mock(spec=Session)
    session = SimpleNamespace(user_id=10)
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=team),
    )
    monkeypatch.setattr(
        tasks_service,
        "is_team_member",
        Mock(return_value=is_member),
    )

    with pytest.raises(TaskAccessDeniedError):
        TaskService().get_all_tasks(db, session, TaskQuery(team_id=20))


def test_get_all_tasks_rejects_invalid_assignee(monkeypatch):
    db = Mock(spec=Session)
    session = SimpleNamespace(user_id=10)
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=SimpleNamespace(is_active=True)),
    )
    monkeypatch.setattr(tasks_service, "is_team_member", Mock(return_value=True))
    monkeypatch.setattr(
        tasks_service,
        "get_team_member_by_id",
        Mock(return_value=None),
    )

    with pytest.raises(InvalidTaskError, match="Invalid assignee_member_id"):
        TaskService().get_all_tasks(
            db,
            session,
            TaskQuery(team_id=20, assignee_member_id=30),
        )


def test_create_task_assigns_first_backlog_task_to_creator(monkeypatch):
    db = Mock(spec=Session)
    payload = TaskCreate(title="First task", should_review=False)
    task = SimpleNamespace(id=1)
    get_creator = Mock(return_value=SimpleNamespace(id=40))
    lock_positions = Mock()
    get_last_position = Mock(return_value=None)
    insert_task = Mock(return_value=task)
    ordered_calls = Mock()
    ordered_calls.attach_mock(get_creator, "creator")
    ordered_calls.attach_mock(lock_positions, "lock")
    ordered_calls.attach_mock(get_last_position, "last_position")
    monkeypatch.setattr(tasks_service, "get_team_member", get_creator)
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(
        tasks_service,
        "get_last_task_position",
        get_last_position,
    )
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    result = TaskService().create_task(db, 20, 10, payload)

    get_creator.assert_called_once_with(db, 20, 10)
    lock_positions.assert_called_once_with(db, 20)
    get_last_position.assert_called_once_with(
        db,
        TaskFilters(
            team_id=20,
            statuses=[TaskStatus.BACKLOG],
            assignee_member_id=None,
        ),
    )
    assert ordered_calls.mock_calls == [
        call.creator(db, 20, 10),
        call.lock(db, 20),
        call.last_position(
            db,
            TaskFilters(
                team_id=20,
                statuses=[TaskStatus.BACKLOG],
                assignee_member_id=None,
            ),
        ),
    ]
    insert_task.assert_called_once_with(
        db,
        20,
        40,
        payload.model_copy(update={"assignee_member_id": 40}),
        tasks_service.TASK_POSITION_GAP,
        None,
    )
    assert result is task
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_create_task_validates_assignee_and_reviewer(monkeypatch):
    db = Mock(spec=Session)
    payload = TaskCreate(
        title="Reviewed task",
        assignee_member_id=50,
        reviewer_member_id=60,
    )
    get_creator = Mock(return_value=SimpleNamespace(id=40))
    get_member_by_id = Mock(return_value=SimpleNamespace())
    lock_positions = Mock()
    get_last_position = Mock(return_value=3)
    insert_task = Mock(return_value=SimpleNamespace(id=1))
    ordered_calls = Mock()
    ordered_calls.attach_mock(get_creator, "creator")
    ordered_calls.attach_mock(get_member_by_id, "member")
    ordered_calls.attach_mock(lock_positions, "lock")
    ordered_calls.attach_mock(get_last_position, "last_position")
    monkeypatch.setattr(tasks_service, "get_team_member", get_creator)
    monkeypatch.setattr(
        tasks_service,
        "get_team_member_by_id",
        get_member_by_id,
    )
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(tasks_service, "get_last_task_position", get_last_position)
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    TaskService().create_task(db, 20, 10, payload)

    get_member_by_id.assert_has_calls(
        [call(db, 20, 50), call(db, 20, 60)],
        any_order=True,
    )
    assert get_member_by_id.call_count == 2
    lock_positions.assert_called_once_with(db, 20)
    assert ordered_calls.mock_calls == [
        call.creator(db, 20, 10),
        call.member(db, 20, 50),
        call.member(db, 20, 60),
        call.lock(db, 20),
        call.last_position(
            db,
            TaskFilters(
                team_id=20,
                statuses=[TaskStatus.BACKLOG],
                assignee_member_id=None,
            ),
        ),
    ]
    insert_task.assert_called_once_with(
        db,
        20,
        40,
        payload,
        3 + tasks_service.TASK_POSITION_GAP,
        None,
    )


def test_create_task_rejects_non_member_creator(monkeypatch):
    db = Mock(spec=Session)
    lock_positions = Mock()
    monkeypatch.setattr(tasks_service, "get_team_member", Mock(return_value=None))
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)

    with pytest.raises(TeamMembershipError):
        TaskService().create_task(
            db,
            20,
            10,
            TaskCreate(title="First task", should_review=False),
        )

    lock_positions.assert_not_called()


def test_create_task_rejects_invalid_assignee(monkeypatch):
    db = Mock(spec=Session)
    lock_positions = Mock()
    insert_task = Mock()
    monkeypatch.setattr(
        tasks_service,
        "get_team_member",
        Mock(return_value=SimpleNamespace(id=40)),
    )
    monkeypatch.setattr(
        tasks_service,
        "get_team_member_by_id",
        Mock(return_value=None),
    )
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    with pytest.raises(TeamMembershipError, match="Invalid assignee"):
        TaskService().create_task(
            db,
            20,
            10,
            TaskCreate(
                title="Assigned task",
                assignee_member_id=50,
                should_review=False,
            ),
        )

    lock_positions.assert_not_called()
    insert_task.assert_not_called()


def test_create_task_rejects_invalid_reviewer(monkeypatch):
    db = Mock(spec=Session)
    lock_positions = Mock()
    insert_task = Mock()
    monkeypatch.setattr(
        tasks_service,
        "get_team_member",
        Mock(return_value=SimpleNamespace(id=40)),
    )
    monkeypatch.setattr(
        tasks_service,
        "get_team_member_by_id",
        Mock(return_value=None),
    )
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    with pytest.raises(TeamMembershipError, match="Invalid reviewer"):
        TaskService().create_task(
            db,
            20,
            10,
            TaskCreate(
                title="Reviewed task",
                reviewer_member_id=60,
            ),
        )

    lock_positions.assert_not_called()
    insert_task.assert_not_called()


def test_create_in_progress_task_sets_start_time(monkeypatch):
    db = Mock(spec=Session)
    now = datetime(2026, 7, 25, 10, 30, tzinfo=timezone.utc)
    datetime_mock = Mock(wraps=datetime)
    datetime_mock.now.return_value = now
    payload = TaskCreate(
        title="Started task",
        status=TaskStatus.IN_PROGRESS,
        should_review=False,
    )
    task = SimpleNamespace(id=1)
    get_creator = Mock(return_value=SimpleNamespace(id=40))
    lock_positions = Mock()
    get_team = Mock(return_value=SimpleNamespace(is_active=True))
    get_limit = Mock(return_value=3)
    count_tasks = Mock(return_value=2)
    get_last_position = Mock(return_value=None)
    insert_task = Mock(return_value=task)
    ordered_calls = Mock()
    ordered_calls.attach_mock(get_creator, "creator")
    ordered_calls.attach_mock(lock_positions, "lock")
    ordered_calls.attach_mock(get_team, "team")
    ordered_calls.attach_mock(get_limit, "limit")
    ordered_calls.attach_mock(count_tasks, "capacity_count")
    ordered_calls.attach_mock(get_last_position, "last_position")
    monkeypatch.setattr(tasks_service, "datetime", datetime_mock)
    monkeypatch.setattr(tasks_service, "get_team_member", get_creator)
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(tasks_service, "get_team_by_id", get_team)
    monkeypatch.setattr(tasks_service, "get_in_progress_limit", get_limit)
    monkeypatch.setattr(tasks_service, "count_team_tasks_by_status", count_tasks)
    monkeypatch.setattr(tasks_service, "get_last_task_position", get_last_position)
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    result = TaskService().create_task(db, 20, 10, payload)

    lock_positions.assert_called_once_with(db, 20)
    assert ordered_calls.mock_calls == [
        call.creator(db, 20, 10),
        call.lock(db, 20),
        call.team(db, 20),
        call.limit(db),
        call.capacity_count(db, 20, TaskStatus.IN_PROGRESS),
        call.last_position(
            db,
            TaskFilters(
                team_id=20,
                statuses=[TaskStatus.IN_PROGRESS],
                assignee_member_id=None,
            ),
        ),
    ]
    insert_task.assert_called_once_with(
        db,
        20,
        40,
        payload.model_copy(update={"assignee_member_id": 40}),
        tasks_service.TASK_POSITION_GAP,
        now,
    )
    assert result is task


def test_create_in_progress_task_rejects_reached_limit(monkeypatch):
    db = Mock(spec=Session)
    lock_positions = Mock()
    insert_task = Mock()
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=SimpleNamespace(is_active=True)),
    )
    monkeypatch.setattr(tasks_service, "get_in_progress_limit", Mock(return_value=3))
    monkeypatch.setattr(
        tasks_service,
        "count_team_tasks_by_status",
        Mock(return_value=3),
    )
    monkeypatch.setattr(
        tasks_service,
        "get_team_member",
        Mock(return_value=SimpleNamespace(id=40)),
    )
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    with pytest.raises(ApiConflictError, match="IN_PROGRESS limit reached"):
        TaskService().create_task(
            db,
            20,
            10,
            TaskCreate(
                title="Started task",
                status=TaskStatus.IN_PROGRESS,
                should_review=False,
            ),
        )

    lock_positions.assert_called_once_with(db, 20)
    insert_task.assert_not_called()


def test_create_in_progress_task_requires_active_team(monkeypatch):
    db = Mock(spec=Session)
    lock_positions = Mock()
    monkeypatch.setattr(
        tasks_service,
        "get_team_member",
        Mock(return_value=SimpleNamespace(id=40)),
    )
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=SimpleNamespace(is_active=False)),
    )

    with pytest.raises(TeamInactiveError):
        TaskService().create_task(
            db,
            20,
            10,
            TaskCreate(
                title="Started task",
                status=TaskStatus.IN_PROGRESS,
                should_review=False,
            ),
        )

    lock_positions.assert_called_once_with(db, 20)


def test_create_in_progress_task_requires_app_configuration(monkeypatch):
    db = Mock(spec=Session)
    lock_positions = Mock()
    monkeypatch.setattr(
        tasks_service,
        "get_team_member",
        Mock(return_value=SimpleNamespace(id=40)),
    )
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=SimpleNamespace(is_active=True)),
    )
    monkeypatch.setattr(tasks_service, "get_in_progress_limit", Mock(return_value=None))

    with pytest.raises(ApiInternalServerError, match="App configuration is missing"):
        TaskService().create_task(
            db,
            20,
            10,
            TaskCreate(
                title="Started task",
                status=TaskStatus.IN_PROGRESS,
                should_review=False,
            ),
        )

    lock_positions.assert_called_once_with(db, 20)


def test_create_task_rejects_exhausted_sparse_position(monkeypatch):
    db = Mock(spec=Session)
    lock_positions = Mock()
    insert_task = Mock()
    monkeypatch.setattr(
        tasks_service,
        "get_team_member",
        Mock(return_value=SimpleNamespace(id=40)),
    )
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(
        tasks_service,
        "get_last_task_position",
        Mock(
            return_value=(
                tasks_service.MAX_TASK_POSITION - tasks_service.TASK_POSITION_GAP + 1
            )
        ),
    )
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    with pytest.raises(
        ApiConflictError,
        match="No position is available in the destination column",
    ):
        TaskService().create_task(
            db,
            20,
            10,
            TaskCreate(title="Overflow task", should_review=False),
        )

    lock_positions.assert_called_once_with(db, 20)
    insert_task.assert_not_called()


def test_update_task_passes_partial_update_and_keeps_existing_review(monkeypatch):
    db = Mock(spec=Session)
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=60,
        should_review=True,
        review_date=date.max,
    )
    updated_task = SimpleNamespace(id=1, title="Updated title")
    update_task = Mock(return_value=updated_task)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    result = TaskService().update_task(
        db,
        task,
        TaskUpdate(title="Updated title"),
    )

    update_task.assert_called_once_with(task, {"title": "Updated title"})
    assert result is updated_task
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_update_task_accepts_valid_assignee(monkeypatch):
    db = Mock(spec=Session)
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=None,
        should_review=False,
        review_date=None,
    )
    get_member = Mock(return_value=SimpleNamespace(id=50))
    update_task = Mock(return_value=task)
    monkeypatch.setattr(tasks_service, "get_team_member_by_id", get_member)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    TaskService().update_task(db, task, TaskUpdate(assignee_member_id=50))

    get_member.assert_called_once_with(db, 20, 50)
    update_task.assert_called_once_with(task, {"assignee_member_id": 50})


def test_update_task_accepts_cleared_assignee(monkeypatch):
    db = Mock(spec=Session)
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=None,
        should_review=False,
        review_date=None,
    )
    get_member = Mock()
    update_task = Mock(return_value=task)
    monkeypatch.setattr(tasks_service, "get_team_member_by_id", get_member)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    TaskService().update_task(db, task, TaskUpdate(assignee_member_id=None))

    get_member.assert_not_called()
    update_task.assert_called_once_with(task, {"assignee_member_id": None})


def test_update_task_rejects_invalid_assignee(monkeypatch):
    db = Mock(spec=Session)
    update_task = Mock()
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=None,
        should_review=False,
        review_date=None,
    )
    monkeypatch.setattr(
        tasks_service,
        "get_team_member_by_id",
        Mock(return_value=None),
    )
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(InvalidTaskError, match="Invalid assignee_member_id"):
        TaskService().update_task(db, task, TaskUpdate(assignee_member_id=50))

    update_task.assert_not_called()


def test_update_task_accepts_reviewer_for_reviewed_task(monkeypatch):
    db = Mock(spec=Session)
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=None,
        should_review=False,
        review_date=None,
    )
    get_member = Mock(return_value=SimpleNamespace(id=60))
    update_task = Mock(return_value=task)
    monkeypatch.setattr(tasks_service, "get_team_member_by_id", get_member)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    TaskService().update_task(
        db,
        task,
        TaskUpdate(reviewer_member_id=60, should_review=True),
    )

    get_member.assert_called_once_with(db, 20, 60)
    update_task.assert_called_once_with(
        task,
        {"reviewer_member_id": 60, "should_review": True},
    )


def test_update_task_accepts_cleared_reviewer(monkeypatch):
    db = Mock(spec=Session)
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=60,
        should_review=True,
        review_date=date.max,
    )
    get_member = Mock()
    update_task = Mock(return_value=task)
    monkeypatch.setattr(tasks_service, "get_team_member_by_id", get_member)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    TaskService().update_task(
        db,
        task,
        TaskUpdate(
            reviewer_member_id=None,
            review_date=None,
            should_review=False,
        ),
    )

    get_member.assert_not_called()
    update_task.assert_called_once_with(
        task,
        {
            "reviewer_member_id": None,
            "review_date": None,
            "should_review": False,
        },
    )


def test_update_task_rejects_invalid_reviewer(monkeypatch):
    db = Mock(spec=Session)
    update_task = Mock()
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=None,
        should_review=False,
        review_date=None,
    )
    monkeypatch.setattr(
        tasks_service,
        "get_team_member_by_id",
        Mock(return_value=None),
    )
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(InvalidTaskError, match="Invalid reviewer_member_id"):
        TaskService().update_task(
            db,
            task,
            TaskUpdate(reviewer_member_id=60, should_review=True),
        )

    update_task.assert_not_called()


def test_update_task_rejects_review_date_without_review(monkeypatch):
    db = Mock(spec=Session)
    update_task = Mock()
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=None,
        should_review=False,
        review_date=None,
    )
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(
        ApiConflictError,
        match="Task with no review cannot have a review date",
    ):
        TaskService().update_task(
            db,
            task,
            TaskUpdate(
                review_date=date.max,
                should_review=False,
            ),
        )

    update_task.assert_not_called()


def test_update_task_rejects_review_without_reviewer(monkeypatch):
    db = Mock(spec=Session)
    update_task = Mock()
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=None,
        should_review=False,
        review_date=None,
    )
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(ApiConflictError, match="Can't review task with no reviewer"):
        TaskService().update_task(db, task, TaskUpdate(should_review=True))

    update_task.assert_not_called()


def test_update_task_rejects_reviewer_without_review(monkeypatch):
    db = Mock(spec=Session)
    update_task = Mock()
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.BACKLOG,
        reviewer_member_id=60,
        should_review=True,
        review_date=None,
    )
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(
        ApiConflictError,
        match="Can't assign reviewer to task that shouldn't be reviewed",
    ):
        TaskService().update_task(db, task, TaskUpdate(should_review=False))

    update_task.assert_not_called()


def test_update_task_keeps_task_in_review_reviewable(monkeypatch):
    db = Mock(spec=Session)
    update_task = Mock()
    task = SimpleNamespace(
        team_id=20,
        status=TaskStatus.REVIEW,
        reviewer_member_id=60,
        should_review=True,
        review_date=None,
    )
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(
        ApiConflictError,
        match="A task in REVIEW must remain reviewable",
    ):
        TaskService().update_task(db, task, TaskUpdate(should_review=False))

    update_task.assert_not_called()


@pytest.mark.parametrize(
    (
        "source_status",
        "target_status",
        "expected_started_at",
        "expected_reviewed_at",
        "expected_completed_at",
        "expected_returned_count",
        "expected_reopened_count",
    ),
    [
        (
            TaskStatus.REVIEW,
            TaskStatus.IN_PROGRESS,
            _MOVED_AT,
            None,
            None,
            3,
            3,
        ),
        (TaskStatus.REVIEW, TaskStatus.TODO, None, None, None, 3, 3),
        (TaskStatus.REVIEW, TaskStatus.BACKLOG, None, None, None, 3, 3),
        (
            TaskStatus.DONE,
            TaskStatus.REVIEW,
            _STARTED_AT,
            _MOVED_AT,
            None,
            2,
            4,
        ),
        (
            TaskStatus.DONE,
            TaskStatus.IN_PROGRESS,
            _MOVED_AT,
            None,
            None,
            2,
            4,
        ),
        (TaskStatus.DONE, TaskStatus.TODO, None, None, None, 2, 4),
        (TaskStatus.DONE, TaskStatus.BACKLOG, None, None, None, 2, 4),
    ],
    ids=[
        "SVC-001-review-to-in-progress",
        "SVC-002-review-to-todo",
        "SVC-002-review-to-backlog",
        "SVC-003-done-to-review",
        "SVC-004-done-to-in-progress",
        "SVC-005-done-to-todo",
        "SVC-005-done-to-backlog",
    ],
)
def test_move_task_updates_backward_lifecycle(
    monkeypatch,
    source_status,
    target_status,
    expected_started_at,
    expected_reviewed_at,
    expected_completed_at,
    expected_returned_count,
    expected_reopened_count,
):
    db = Mock(spec=Session)
    task = _task_for_move(
        source_status,
        completed_at=_COMPLETED_AT if source_status == TaskStatus.DONE else None,
    )
    successor = SimpleNamespace(id=2, position=4000)
    lock_positions = Mock()
    get_neighbors = Mock(return_value=(None, successor))
    update_task = Mock(return_value=task)
    datetime_mock = Mock(wraps=datetime)
    datetime_mock.now.return_value = _MOVED_AT
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(tasks_service, "get_destination_neighbors", get_neighbors)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)
    monkeypatch.setattr(tasks_service, "datetime", datetime_mock)
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=SimpleNamespace(is_active=True)),
    )
    monkeypatch.setattr(tasks_service, "get_in_progress_limit", Mock(return_value=3))
    monkeypatch.setattr(
        tasks_service,
        "count_team_tasks_by_status",
        Mock(return_value=0),
    )

    result = TaskService().move_task(
        db,
        task,
        TaskMove(target_status=target_status),
    )

    lock_positions.assert_called_once_with(db, 20)
    db.refresh.assert_called_once_with(task)
    get_neighbors.assert_called_once_with(db, 20, target_status, None, 1)
    update_task.assert_called_once_with(
        task,
        {
            "started_working_at": expected_started_at,
            "submitted_for_review_at": expected_reviewed_at,
            "completed_at": expected_completed_at,
            "returned_count": expected_returned_count,
            "reopened_count": expected_reopened_count,
            "status": target_status,
            "position": 2000,
        },
    )
    assert "blocked_count" not in update_task.call_args.args[1]
    assert result is task


@pytest.mark.parametrize(
    ("source_status", "target_status", "anchor", "successor", "expected_updates"),
    [
        (
            TaskStatus.BACKLOG,
            TaskStatus.TODO,
            None,
            SimpleNamespace(id=2, position=4000),
            {
                "started_working_at": None,
                "submitted_for_review_at": None,
                "completed_at": None,
                "returned_count": 2,
                "reopened_count": 3,
                "status": TaskStatus.TODO,
                "position": 2000,
            },
        ),
        (
            TaskStatus.TODO,
            TaskStatus.TODO,
            SimpleNamespace(id=2, position=1000),
            SimpleNamespace(id=3, position=4000),
            {"position": 2500},
        ),
    ],
    ids=["SVC-006-forward-transition", "SVC-006-same-status-reorder"],
)
def test_move_task_keeps_counters_stable(
    monkeypatch,
    source_status,
    target_status,
    anchor,
    successor,
    expected_updates,
):
    db = Mock(spec=Session)
    task = _task_for_move(
        source_status,
        started_working_at=None,
        submitted_for_review_at=None,
        completed_at=None,
    )
    update_task = Mock(return_value=task)
    monkeypatch.setattr(tasks_service, "lock_task_positions", Mock())
    monkeypatch.setattr(
        tasks_service,
        "get_destination_neighbors",
        Mock(return_value=(anchor, successor)),
    )
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    result = TaskService().move_task(
        db,
        task,
        TaskMove(
            target_status=target_status,
            anchor_task_id=anchor.id if anchor is not None else None,
        ),
    )

    update_task.assert_called_once_with(task, expected_updates)
    assert "blocked_count" not in expected_updates
    assert task.returned_count == 2
    assert task.reopened_count == 3
    assert task.blocked_count == 4
    assert result is task


def test_SVC_007_move_task_rejects_review_for_non_reviewable_task(monkeypatch):
    db = Mock(spec=Session)
    task = _task_for_move(
        TaskStatus.IN_PROGRESS,
        should_review=False,
        submitted_for_review_at=None,
        completed_at=None,
    )
    get_neighbors = Mock()
    update_task = Mock()
    monkeypatch.setattr(tasks_service, "lock_task_positions", Mock())
    monkeypatch.setattr(tasks_service, "get_destination_neighbors", get_neighbors)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(
        InvalidTaskError,
        match="A task without review cannot enter REVIEW",
    ):
        TaskService().move_task(
            db,
            task,
            TaskMove(target_status=TaskStatus.REVIEW),
        )

    get_neighbors.assert_not_called()
    update_task.assert_not_called()


def test_SVC_008_move_task_returns_refreshed_task_for_self_anchor(monkeypatch):
    db = Mock(spec=Session)
    task = _task_for_move(
        TaskStatus.BACKLOG,
        started_working_at=None,
        submitted_for_review_at=None,
        completed_at=None,
    )
    lock_positions = Mock()
    get_neighbors = Mock()
    get_team = Mock()
    get_limit = Mock()
    count_tasks = Mock()
    update_task = Mock()
    rebalance = Mock()
    ordered_calls = Mock()
    ordered_calls.attach_mock(lock_positions, "lock")
    ordered_calls.attach_mock(db.refresh, "refresh")
    monkeypatch.setattr(tasks_service, "lock_task_positions", lock_positions)
    monkeypatch.setattr(tasks_service, "get_destination_neighbors", get_neighbors)
    monkeypatch.setattr(tasks_service, "get_team_by_id", get_team)
    monkeypatch.setattr(tasks_service, "get_in_progress_limit", get_limit)
    monkeypatch.setattr(tasks_service, "count_team_tasks_by_status", count_tasks)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)
    monkeypatch.setattr(tasks_service, "rebalance_task_column", rebalance)

    result = TaskService().move_task(
        db,
        task,
        TaskMove(target_status=TaskStatus.DONE, anchor_task_id=1),
    )

    assert ordered_calls.mock_calls == [call.lock(db, 20), call.refresh(task)]
    get_neighbors.assert_not_called()
    get_team.assert_not_called()
    get_limit.assert_not_called()
    count_tasks.assert_not_called()
    update_task.assert_not_called()
    rebalance.assert_not_called()
    assert result is task


def test_SVC_009_move_task_returns_task_for_current_adjacency(monkeypatch):
    db = Mock(spec=Session)
    task = _task_for_move(
        TaskStatus.TODO,
        position=2000,
        started_working_at=None,
        submitted_for_review_at=None,
        completed_at=None,
    )
    anchor = SimpleNamespace(id=2, position=1000)
    successor = SimpleNamespace(id=3, position=3000)
    update_task = Mock()
    rebalance = Mock()
    monkeypatch.setattr(tasks_service, "lock_task_positions", Mock())
    monkeypatch.setattr(
        tasks_service,
        "get_destination_neighbors",
        Mock(return_value=(anchor, successor)),
    )
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)
    monkeypatch.setattr(tasks_service, "rebalance_task_column", rebalance)

    result = TaskService().move_task(
        db,
        task,
        TaskMove(target_status=TaskStatus.TODO, anchor_task_id=2),
    )

    update_task.assert_not_called()
    rebalance.assert_not_called()
    assert result is task


@pytest.mark.parametrize(
    ("target_status", "anchor_task_id", "neighbors_are_read"),
    [
        (TaskStatus.IN_PROGRESS, None, False),
        (TaskStatus.TODO, 90, True),
        (TaskStatus.TODO, 91, True),
        (TaskStatus.TODO, 92, True),
    ],
    ids=[
        "SVC-010-forward-skip",
        "SVC-010-missing-anchor",
        "SVC-010-wrong-team-anchor",
        "SVC-010-wrong-status-anchor",
    ],
)
def test_move_task_rejects_invalid_client_input(
    monkeypatch,
    target_status,
    anchor_task_id,
    neighbors_are_read,
):
    db = Mock(spec=Session)
    task = _task_for_move(
        TaskStatus.BACKLOG,
        started_working_at=None,
        submitted_for_review_at=None,
        completed_at=None,
    )
    get_neighbors = Mock(return_value=(None, None))
    update_task = Mock()
    monkeypatch.setattr(tasks_service, "lock_task_positions", Mock())
    monkeypatch.setattr(tasks_service, "get_destination_neighbors", get_neighbors)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(InvalidTaskError):
        TaskService().move_task(
            db,
            task,
            TaskMove(
                target_status=target_status,
                anchor_task_id=anchor_task_id,
            ),
        )

    assert get_neighbors.called is neighbors_are_read
    update_task.assert_not_called()


def test_SVC_011_move_task_rebalances_active_reorder_without_capacity_read(
    monkeypatch,
):
    db = Mock(spec=Session)
    task = _task_for_move(
        TaskStatus.IN_PROGRESS,
        position=3000,
        submitted_for_review_at=None,
        completed_at=None,
    )
    original_anchor = SimpleNamespace(id=2, position=1000)
    original_successor = SimpleNamespace(id=3, position=1001)
    rebalanced_anchor = SimpleNamespace(id=2, position=1000)
    rebalanced_successor = SimpleNamespace(id=3, position=2000)
    get_team = Mock()
    get_limit = Mock()
    count_tasks = Mock()
    rebalance = Mock(return_value=[rebalanced_anchor, rebalanced_successor])
    update_task = Mock(return_value=task)
    monkeypatch.setattr(tasks_service, "lock_task_positions", Mock())
    monkeypatch.setattr(
        tasks_service,
        "get_destination_neighbors",
        Mock(return_value=(original_anchor, original_successor)),
    )
    monkeypatch.setattr(tasks_service, "get_team_by_id", get_team)
    monkeypatch.setattr(tasks_service, "get_in_progress_limit", get_limit)
    monkeypatch.setattr(tasks_service, "count_team_tasks_by_status", count_tasks)
    monkeypatch.setattr(tasks_service, "rebalance_task_column", rebalance)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    result = TaskService().move_task(
        db,
        task,
        TaskMove(target_status=TaskStatus.IN_PROGRESS, anchor_task_id=2),
    )

    get_team.assert_not_called()
    get_limit.assert_not_called()
    count_tasks.assert_not_called()
    rebalance.assert_called_once_with(
        db,
        20,
        TaskStatus.IN_PROGRESS,
        1,
        tasks_service.TASK_POSITION_GAP,
    )
    update_task.assert_called_once_with(task, {"position": 1500})
    assert result is task


def test_move_task_rejects_entry_when_in_progress_limit_is_reached(monkeypatch):
    db = Mock(spec=Session)
    task = _task_for_move(
        TaskStatus.TODO,
        started_working_at=None,
        submitted_for_review_at=None,
        completed_at=None,
    )
    get_neighbors = Mock()
    update_task = Mock()
    monkeypatch.setattr(tasks_service, "lock_task_positions", Mock())
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=SimpleNamespace(is_active=True)),
    )
    monkeypatch.setattr(tasks_service, "get_in_progress_limit", Mock(return_value=3))
    monkeypatch.setattr(
        tasks_service,
        "count_team_tasks_by_status",
        Mock(return_value=3),
    )
    monkeypatch.setattr(tasks_service, "get_destination_neighbors", get_neighbors)
    monkeypatch.setattr(tasks_service, "update_task_repository", update_task)

    with pytest.raises(ApiConflictError, match="IN_PROGRESS limit reached"):
        TaskService().move_task(
            db,
            task,
            TaskMove(target_status=TaskStatus.IN_PROGRESS),
        )

    get_neighbors.assert_not_called()
    update_task.assert_not_called()


def test_get_accessible_task_returns_team_task(monkeypatch):
    db = Mock(spec=Session)
    task = SimpleNamespace(id=1, team_id=20)
    get_task = Mock(return_value=task)
    is_member = Mock(return_value=True)
    get_team = Mock(return_value=SimpleNamespace(is_active=True))
    monkeypatch.setattr(tasks_service, "get_task_by_id", get_task)
    monkeypatch.setattr(tasks_service, "is_team_member", is_member)
    monkeypatch.setattr(tasks_service, "get_team_by_id", get_team)

    result = TaskService().get_accessible_task(db, task_id=1, user_id=10)

    get_task.assert_called_once_with(db, 1)
    is_member.assert_called_once_with(db, 20, 10)
    get_team.assert_called_once_with(db, 20)
    assert result is task


def test_get_accessible_task_requires_existing_task(monkeypatch):
    db = Mock(spec=Session)
    monkeypatch.setattr(tasks_service, "get_task_by_id", Mock(return_value=None))

    with pytest.raises(TaskNotFoundError):
        TaskService().get_accessible_task(db, task_id=1, user_id=10)


def test_get_accessible_task_requires_team_membership(monkeypatch):
    db = Mock(spec=Session)
    monkeypatch.setattr(
        tasks_service,
        "get_task_by_id",
        Mock(return_value=SimpleNamespace(team_id=20)),
    )
    monkeypatch.setattr(tasks_service, "is_team_member", Mock(return_value=False))

    with pytest.raises(TeamMembershipError):
        TaskService().get_accessible_task(db, task_id=1, user_id=10)


def test_get_accessible_task_requires_existing_team(monkeypatch):
    db = Mock(spec=Session)
    monkeypatch.setattr(
        tasks_service,
        "get_task_by_id",
        Mock(return_value=SimpleNamespace(team_id=20)),
    )
    monkeypatch.setattr(tasks_service, "is_team_member", Mock(return_value=True))
    monkeypatch.setattr(tasks_service, "get_team_by_id", Mock(return_value=None))

    with pytest.raises(TeamNotFoundError):
        TaskService().get_accessible_task(db, task_id=1, user_id=10)


def test_get_accessible_task_requires_active_team(monkeypatch):
    db = Mock(spec=Session)
    monkeypatch.setattr(
        tasks_service,
        "get_task_by_id",
        Mock(return_value=SimpleNamespace(team_id=20)),
    )
    monkeypatch.setattr(tasks_service, "is_team_member", Mock(return_value=True))
    monkeypatch.setattr(
        tasks_service,
        "get_team_by_id",
        Mock(return_value=SimpleNamespace(is_active=False)),
    )

    with pytest.raises(TeamInactiveError):
        TaskService().get_accessible_task(db, task_id=1, user_id=10)
