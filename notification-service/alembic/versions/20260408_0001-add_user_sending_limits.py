"""Add user sending limits and usage counters

Revision ID: add_user_sending_limits
Revises: 79dd42d2461a
Create Date: 2026-04-08 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_user_sending_limits'
down_revision: Union[str, None] = '79dd42d2461a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    existing = [row[0] for row in conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='users'"
    ))]
    if 'email_limit' not in existing:
        op.add_column('users', sa.Column('email_limit', sa.Integer(), nullable=True))
    if 'sms_limit' not in existing:
        op.add_column('users', sa.Column('sms_limit', sa.Integer(), nullable=True))
    if 'email_sent' not in existing:
        op.add_column('users', sa.Column('email_sent', sa.Integer(), nullable=False, server_default='0'))
    if 'sms_sent' not in existing:
        op.add_column('users', sa.Column('sms_sent', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('users', 'sms_sent')
    op.drop_column('users', 'email_sent')
    op.drop_column('users', 'sms_limit')
    op.drop_column('users', 'email_limit')
