"""Add created_by_user_id to notifications

Revision ID: add_notification_created_by
Revises: add_user_sending_limits
Create Date: 2026-04-08 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'add_notification_created_by'
down_revision: Union[str, None] = 'add_user_sending_limits'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    existing = [row[0] for row in conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='notifications'"
    ))]
    if 'created_by_user_id' not in existing:
        op.add_column('notifications', sa.Column(
            'created_by_user_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True
        ))


def downgrade() -> None:
    op.drop_column('notifications', 'created_by_user_id')
