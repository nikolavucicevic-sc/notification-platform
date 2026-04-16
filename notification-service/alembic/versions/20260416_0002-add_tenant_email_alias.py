"""Add email_alias to tenants

Revision ID: add_tenant_email_alias
Revises: add_customer_tenant_id
Create Date: 2026-04-16 00:02:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'add_tenant_email_alias'
down_revision: Union[str, None] = 'add_customer_tenant_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tenants', sa.Column('email_alias', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('tenants', 'email_alias')
