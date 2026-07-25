"""Normalize task positions and make their uniqueness deferrable.

Revision ID: 4f6a8b0c2d3e
Revises: 2d4c6e8f0a1b
Create Date: 2026-07-25

"""
from typing import Sequence, Union

from alembic import op


revision: str = "4f6a8b0c2d3e"
down_revision: Union[str, Sequence[str], None] = "2d4c6e8f0a1b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Preserve visible column order while creating sparse, safely bounded positions."""
    # Fail before any ordering mutation if a partition cannot fit in PostgreSQL INTEGER.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM tasks
                GROUP BY team_id, status
                HAVING count(*) > 2147483647 / 1000
            ) THEN
                RAISE EXCEPTION
                    'Cannot normalize task positions: a task column exceeds INTEGER capacity';
            END IF;
        END
        $$
        """
    )
    op.execute(
        "ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'backlog'::task_status"
    )
    op.drop_constraint(
        "uq_task_team_status_position", "tasks", type_="unique"
    )
    op.execute(
        """
        WITH normalized AS (
            SELECT
                id,
                row_number() OVER (
                    PARTITION BY team_id, status
                    ORDER BY position, id
                ) * 1000 AS position
            FROM tasks
        )
        UPDATE tasks
        SET position = normalized.position
        FROM normalized
        WHERE tasks.id = normalized.id
        """
    )
    op.create_unique_constraint(
        "uq_task_team_status_position",
        "tasks",
        ["team_id", "status", "position"],
        deferrable=True,
        initially="IMMEDIATE",
    )


def downgrade() -> None:
    """Restore the TODO default and non-deferrable uniqueness without densifying positions."""
    op.execute(
        "ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'todo'::task_status"
    )
    op.drop_constraint(
        "uq_task_team_status_position", "tasks", type_="unique"
    )
    op.create_unique_constraint(
        "uq_task_team_status_position",
        "tasks",
        ["team_id", "status", "position"],
    )
