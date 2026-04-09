"""Add multi-tenancy: tenants table, tenant_id FKs, SUPER_ADMIN role

Revision ID: add_multitenancy
Revises: add_notification_created_by
Create Date: 2026-04-09 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'add_multitenancy'
down_revision: Union[str, None] = 'add_notification_created_by'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Add SUPER_ADMIN to userrole enum using AUTOCOMMIT so it is visible
    # immediately — PostgreSQL does not allow using a new enum value in the
    # same transaction that added it.
    conn.execute(sa.text("COMMIT"))  # close the current alembic transaction
    conn.execute(sa.text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'SUPER_ADMIN'"))
    conn.execute(sa.text("BEGIN"))  # re-open a transaction for the rest

    # 2. Create tenants table
    existing_tables = [row[0] for row in conn.execute(sa.text(
        "SELECT tablename FROM pg_tables WHERE schemaname='public'"
    ))]
    if 'tenants' not in existing_tables:
        op.create_table(
            'tenants',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('name', sa.String(), nullable=False, unique=True),
            sa.Column('email_limit', sa.Integer(), nullable=True),
            sa.Column('sms_limit', sa.Integer(), nullable=True),
            sa.Column('email_sent', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('sms_sent', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index('ix_tenants_name', 'tenants', ['name'])

    # 3. Create TEST COMPANY tenant and get its ID
    result = conn.execute(sa.text(
        "SELECT id FROM tenants WHERE name = 'TEST COMPANY' LIMIT 1"
    ))
    row = result.fetchone()
    if row is None:
        conn.execute(sa.text(
            "INSERT INTO tenants (id, name, is_active, email_sent, sms_sent) "
            "VALUES (gen_random_uuid(), 'TEST COMPANY', true, 0, 0)"
        ))
        result = conn.execute(sa.text(
            "SELECT id FROM tenants WHERE name = 'TEST COMPANY' LIMIT 1"
        ))
        row = result.fetchone()
    test_company_id = str(row[0])

    # 4. Add tenant_id to users table
    existing_user_cols = [r[0] for r in conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='users'"
    ))]
    if 'tenant_id' not in existing_user_cols:
        op.add_column('users', sa.Column(
            'tenant_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('tenants.id', ondelete='CASCADE'),
            nullable=True
        ))
        op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])

    # 5. Assign all existing non-SUPER_ADMIN users to TEST COMPANY
    conn.execute(sa.text(
        f"UPDATE users SET tenant_id = '{test_company_id}' "
        f"WHERE tenant_id IS NULL AND role != 'SUPER_ADMIN'"
    ))

    # 6. Upgrade existing 'admin' user to SUPER_ADMIN
    conn.execute(sa.text(
        "UPDATE users SET role = 'SUPER_ADMIN', tenant_id = NULL "
        "WHERE username = 'admin'"
    ))

    # 7. Add tenant_id to notifications table
    existing_notif_cols = [r[0] for r in conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_name='notifications'"
    ))]
    if 'tenant_id' not in existing_notif_cols:
        op.add_column('notifications', sa.Column(
            'tenant_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('tenants.id', ondelete='CASCADE'),
            nullable=True
        ))
        op.create_index('ix_notifications_tenant_id', 'notifications', ['tenant_id'])

    # 8. Assign all existing notifications to TEST COMPANY
    conn.execute(sa.text(
        f"UPDATE notifications SET tenant_id = '{test_company_id}' "
        f"WHERE tenant_id IS NULL"
    ))


def downgrade() -> None:
    op.drop_index('ix_notifications_tenant_id', table_name='notifications')
    op.drop_column('notifications', 'tenant_id')
    op.drop_index('ix_users_tenant_id', table_name='users')
    op.drop_column('users', 'tenant_id')
    op.drop_table('tenants')
