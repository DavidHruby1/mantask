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
from backend.app.schemas.task import TaskCreate, TaskFilters, TaskQuery, TaskUpdate
from backend.app.services import tasks as tasks_service
from backend.app.services.tasks import TaskService


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


def test_create_task_assigns_first_todo_task_to_creator(monkeypatch):
    db = Mock(spec=Session)
    payload = TaskCreate(title="First task", should_review=False)
    task = SimpleNamespace(id=1)
    get_creator = Mock(return_value=SimpleNamespace(id=40))
    get_last_position = Mock(return_value=None)
    insert_task = Mock(return_value=task)
    monkeypatch.setattr(tasks_service, "get_team_member", get_creator)
    monkeypatch.setattr(
        tasks_service,
        "get_last_task_position",
        get_last_position,
    )
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    result = TaskService().create_task(db, 20, 10, payload)

    get_creator.assert_called_once_with(db, 20, 10)
    get_last_position.assert_called_once_with(
        db,
        TaskFilters(
            team_id=20,
            statuses=[TaskStatus.TODO],
            assignee_member_id=None,
        ),
    )
    insert_task.assert_called_once_with(
        db,
        20,
        40,
        payload.model_copy(update={"assignee_member_id": 40}),
        1,
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
    get_member_by_id = Mock(return_value=SimpleNamespace())
    insert_task = Mock(return_value=SimpleNamespace(id=1))
    monkeypatch.setattr(
        tasks_service,
        "get_team_member",
        Mock(return_value=SimpleNamespace(id=40)),
    )
    monkeypatch.setattr(
        tasks_service,
        "get_team_member_by_id",
        get_member_by_id,
    )
    monkeypatch.setattr(
        tasks_service,
        "get_last_task_position",
        Mock(return_value=3),
    )
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    TaskService().create_task(db, 20, 10, payload)

    get_member_by_id.assert_has_calls(
        [call(db, 20, 50), call(db, 20, 60)],
        any_order=True,
    )
    assert get_member_by_id.call_count == 2
    insert_task.assert_called_once_with(db, 20, 40, payload, 4, None)


def test_create_task_rejects_non_member_creator(monkeypatch):
    db = Mock(spec=Session)
    monkeypatch.setattr(tasks_service, "get_team_member", Mock(return_value=None))

    with pytest.raises(TeamMembershipError):
        TaskService().create_task(
            db,
            20,
            10,
            TaskCreate(title="First task", should_review=False),
        )


def test_create_task_rejects_invalid_assignee(monkeypatch):
    db = Mock(spec=Session)
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

    insert_task.assert_not_called()


def test_create_task_rejects_invalid_reviewer(monkeypatch):
    db = Mock(spec=Session)
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
    insert_task = Mock(return_value=task)
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
        Mock(return_value=2),
    )
    monkeypatch.setattr(
        tasks_service,
        "get_team_member",
        Mock(return_value=SimpleNamespace(id=40)),
    )
    monkeypatch.setattr(
        tasks_service,
        "get_last_task_position",
        Mock(return_value=None),
    )
    monkeypatch.setattr(tasks_service, "insert_task", insert_task)

    result = TaskService().create_task(db, 20, 10, payload)

    tasks_service.count_team_tasks_by_status.assert_called_once_with(
        db,
        20,
        TaskStatus.IN_PROGRESS,
    )
    insert_task.assert_called_once_with(
        db,
        20,
        40,
        payload.model_copy(update={"assignee_member_id": 40}),
        1,
        now,
    )
    assert result is task


def test_create_in_progress_task_rejects_reached_limit(monkeypatch):
    db = Mock(spec=Session)
    insert_task = Mock()
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

    insert_task.assert_not_called()


def test_create_in_progress_task_requires_existing_team(monkeypatch):
    db = Mock(spec=Session)
    monkeypatch.setattr(tasks_service, "get_team_by_id", Mock(return_value=None))

    with pytest.raises(TeamNotFoundError):
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


def test_create_in_progress_task_requires_active_team(monkeypatch):
    db = Mock(spec=Session)
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


def test_create_in_progress_task_requires_app_configuration(monkeypatch):
    db = Mock(spec=Session)
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


def test_update_task_passes_partial_update_and_keeps_existing_review(monkeypatch):
    db = Mock(spec=Session)
    task = SimpleNamespace(
        team_id=20,
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
