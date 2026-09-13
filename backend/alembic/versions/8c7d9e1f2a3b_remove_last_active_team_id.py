"""Remove server-side active team selection.

Revision ID: 8c7d9e1f2a3b
Revises: 15aa3619b032
Create Date: 2026-09-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c7d9e1f2a3b"
down_revision: Union[str, Sequence[str], None] = "15aa3619b032"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("app_users", "last_active_team_id")


def downgrade() -> None:
    op.add_column(
        "app_users",
        sa.Column("last_active_team_id", sa.Integer(), nullable=True),
    )
