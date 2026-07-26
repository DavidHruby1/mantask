"""Add the backlog task status outside a transaction.

Revision ID: 2d4c6e8f0a1b
Revises: 69b849fd1043
Create Date: 2026-07-25

"""
from typing import Sequence, Union

from alembic import op


revision: str = "2d4c6e8f0a1b"
down_revision: Union[str, Sequence[str], None] = "69b849fd1043"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add BACKLOG recoverably because PostgreSQL 11 cannot use a new enum value transactionally."""
    with op.get_context().autocommit_block():
        op.execute(
            "ALTER TYPE task_status ADD VALUE IF NOT EXISTS 'backlog' BEFORE 'todo'"
        )


def downgrade() -> None:
    """Remove BACKLOG without rewriting task data, refusing downgrade while rows use it."""
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM tasks WHERE status::text = 'backlog') THEN
                RAISE EXCEPTION
                    'Cannot remove task_status value backlog while BACKLOG tasks exist';
            END IF;
        END
        $$
        """
    )
    op.execute("ALTER TABLE tasks ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TYPE task_status RENAME TO task_status_with_backlog")
    op.execute(
        "CREATE TYPE task_status AS ENUM ('todo', 'in_progress', 'review', 'done')"
    )
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status TYPE task_status
        USING status::text::task_status
        """
    )
    op.execute("DROP TYPE task_status_with_backlog")
    op.execute(
        "ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'todo'::task_status"
    )
