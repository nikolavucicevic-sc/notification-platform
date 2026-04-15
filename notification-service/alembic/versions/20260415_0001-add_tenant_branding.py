"""Add tenant branding: display_name and reply_to_email

Revision ID: add_tenant_branding
Revises: add_multitenancy
Create Date: 2026-04-15 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'add_tenant_branding'
down_revision: Union[str, None] = 'add_multitenancy'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tenants', sa.Column('display_name', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('reply_to_email', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('tenants', 'reply_to_email')
    op.drop_column('tenants', 'display_name')