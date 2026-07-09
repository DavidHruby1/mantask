from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from backend.app.models.enums import TaskStatus
from backend.app.schemas.task import TaskCreate, TaskUpdate


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

def test_task_update_rejects_blank_title_and_blank_layer():
    with pytest.raises(ValidationError):
        TaskUpdate(title="   ")

    with pytest.raises(ValidationError):
        TaskUpdate(layer="     ")

def test_task_update_validates_date():
    with pytest.raises(ValidationError):
        TaskUpdate(review_date=date.today() - timedelta(days=1))

    with pytest.raises(ValidationError):
        TaskUpdate(due_date=date.today() - timedelta(days=1))

    TaskUpdate(due_date=date.today())
    TaskUpdate(review_date=date.today())
