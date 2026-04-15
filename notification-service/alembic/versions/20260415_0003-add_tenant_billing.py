"""Add tenant billing: plan tier, stripe_customer_id, stripe_subscription_id

Revision ID: add_tenant_billing
Revises: add_password_reset_tokens
Create Date: 2026-04-15 00:03:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'add_tenant_billing'
down_revision: Union[str, None] = 'add_password_reset_tokens'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE plantier AS ENUM ('FREE', 'PRO', 'BUSINESS')")
    op.add_column('tenants', sa.Column('plan', sa.Enum('FREE', 'PRO', 'BUSINESS', name='plantier'), nullable=False, server_default='FREE'))
    op.add_column('tenants', sa.Column('stripe_customer_id', sa.String(), nullable=True, unique=True))
    op.add_column('tenants', sa.Column('stripe_subscription_id', sa.String(), nullable=True, unique=True))


def downgrade() -> None:
    op.drop_column('tenants', 'stripe_subscription_id')
    op.drop_column('tenants', 'stripe_customer_id')
    op.drop_column('tenants', 'plan')
    op.execute("DROP TYPE plantier")
