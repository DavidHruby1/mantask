from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from backend.app.models.enums import TaskStatus
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskFilterFields


# TaskCreate schema testing
def test_task_create_strips_title_and_normalizes_layer():
    task = TaskCreate(
        title="  Fix login  ",
        description=None,
        layer="  Backend  ",
        should_review=False
    )

    assert task.title == "Fix login"
    assert task.layer == "backend"
    assert task.status == TaskStatus.TODO


def test_task_create_rejects_blank_title():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="   ", 
            description=None,
            layer=None,
            should_review=False
        )


def test_task_create_rejects_blank_layer():
    with pytest.raises(ValidationError):
        TaskCreate(
            title=" Add layer tests", 
            description=None,
            layer="     ",
            should_review=False
        )


def test_task_create_validates_date():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="Add layer tests", 
            description=None,
            layer=None,
            should_review=True,
            reviewer_member_id=1,
            review_date=date.today() - timedelta(days=1)
        )

    with pytest.raises(ValidationError):
        TaskCreate(
            title="Add layer tests", 
            description=None,
            layer=None,
            should_review=False,
            due_date=date.today() - timedelta(days=1)
        )

    TaskCreate(
        title="Add layer tests", 
        description=None,
        layer=None,
        should_review=True,
        reviewer_member_id=1,
        due_date=date.today()
    )

    TaskCreate(
        title="Add layer tests", 
        description=None,
        layer=None,
        should_review=True,
        reviewer_member_id=1,
        review_date=date.today()
    )


def test_task_create_validates_status():
    with pytest.raises(ValidationError):
        TaskCreate.model_validate({
            "title": "Add task tests",
            "description": None,
            "layer": None,
            "status": "finished",
            "should_review": False
        })

    with pytest.raises(ValidationError):
        TaskCreate(
            title="Add task tests",
            description=None,
            layer=None,
            status=TaskStatus.DONE,
            should_review=False
        )

    TaskCreate(
        title="Add task tests",
        description=None,
        layer=None,
        status=TaskStatus.IN_PROGRESS,
        should_review=False
    )


def test_task_create_validates_review_rules():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="Add task tests",
            description=None,
            layer=None,
            should_review=True,
            reviewer_member_id=None
        )

    with pytest.raises(ValidationError):
        TaskCreate(
            title="Add task tests",
            description=None,
            layer=None,
            should_review=False,
            reviewer_member_id=1
        )

    with pytest.raises(ValidationError):
        TaskCreate(
            title="Add task tests",
            description=None,
            layer=None,
            should_review=False,
            review_date=date.today()
        )

    TaskCreate(
        title="Add task tests",
        description=None,
        layer=None,
        should_review=True,
        reviewer_member_id=1
    )

    TaskCreate(
        title="Add task tests",
        description=None,
        layer=None,
        should_review=False,
        reviewer_member_id=None
    )


# TaskUpdate schema testing
def test_task_update_strips_title_and_normalizes_layer():
    task = TaskUpdate(
        title="  Fix login  ",
        layer="  Backend  "
    )

    assert task.title == "Fix login"
    assert task.layer == "backend"


@pytest.mark.parametrize("field", ["title", "layer"])
def test_task_update_rejects_blank_title_or_layer(field):
    with pytest.raises(ValidationError):
        TaskUpdate(**{field: "   "})


def test_task_update_rejects_explicit_null_title():
    with pytest.raises(ValidationError, match="Title cannot be null"):
        TaskUpdate(title=None)


def test_task_update_allows_omitted_title():
    task = TaskUpdate()

    assert "title" not in task.model_fields_set


@pytest.mark.parametrize("field", ["review_date", "due_date"])
def test_task_update_rejects_past_date(field):
    with pytest.raises(ValidationError):
        TaskUpdate(**{field: date.today() - timedelta(days=1)})


@pytest.mark.parametrize("field", ["review_date", "due_date"])
def test_task_update_accepts_today(field):
    TaskUpdate(**{field: date.today()})


# TaskFilterFields schema testing
def test_task_filter_fields_normalizes_statuses():
    filter_fields = TaskFilterFields(statuses=["todo", "in_progress"])
    assert filter_fields.statuses == [TaskStatus.TODO, TaskStatus.IN_PROGRESS]


def test_task_filter_fields_preserves_empty_statuses():
    filter_fields = TaskFilterFields(statuses=[])
    assert filter_fields.statuses == []


def test_task_filter_fields_defaults_to_empty_statuses():
    filter_fields = TaskFilterFields()
    assert filter_fields.statuses == []
