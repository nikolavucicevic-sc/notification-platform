"""Add tenant_id to customers; drop global email unique constraint

Revision ID: add_customer_tenant_id
Revises: add_tenant_billing
Create Date: 2026-04-16 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'add_customer_tenant_id'
down_revision: Union[str, None] = 'add_tenant_billing'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the global unique constraint on email — uniqueness is now per-tenant
    op.drop_constraint('customers_email_key', 'customers', type_='unique')
    # Add tenant_id FK
    op.add_column('customers', sa.Column(
        'tenant_id',
        postgresql.UUID(as_uuid=True),
        sa.ForeignKey('tenants.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    ))
    # Add per-tenant unique constraint on (tenant_id, email)
    op.create_unique_constraint('uq_customers_tenant_email', 'customers', ['tenant_id', 'email'])


def downgrade() -> None:
    op.drop_constraint('uq_customers_tenant_email', 'customers', type_='unique')
    op.drop_column('customers', 'tenant_id')
    op.create_unique_constraint('customers_email_key', 'customers', ['email'])
