"""add email automation tables

Revision ID: 0004_add_email_automation_tables
Revises: 0003_add_job_status_history
Create Date: 2026-05-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_add_email_automation_tables"
down_revision = "0003_add_job_status_history"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "email_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=False),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=False),
        sa.Column("access_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_email_connections_user_id_users"),
        sa.UniqueConstraint("user_id", "provider", name="uq_email_connections_user_provider"),
    )
    op.create_index("ix_email_connections_id", "email_connections", ["id"])
    op.create_index("ix_email_connections_user_id", "email_connections", ["user_id"])

    op.create_table(
        "email_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("message_id", sa.String(length=255), nullable=False),
        sa.Column("thread_id", sa.String(length=255), nullable=True),
        sa.Column("sender", sa.String(length=320), nullable=True),
        sa.Column("subject", sa.String(length=500), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("detected_company", sa.String(length=160), nullable=True),
        sa.Column("detected_job_title", sa.String(length=200), nullable=True),
        sa.Column("detected_status", sa.String(length=32), nullable=True),
        sa.Column("processing_status", sa.String(length=40), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], name="fk_email_events_job_id_jobs"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_email_events_user_id_users"),
        sa.UniqueConstraint("user_id", "provider", "message_id", name="uq_email_events_user_provider_message"),
    )
    op.create_index("ix_email_events_id", "email_events", ["id"])
    op.create_index("ix_email_events_user_id", "email_events", ["user_id"])
    op.create_index("ix_email_events_job_id", "email_events", ["job_id"])


def downgrade():
    op.drop_index("ix_email_events_job_id", table_name="email_events")
    op.drop_index("ix_email_events_user_id", table_name="email_events")
    op.drop_index("ix_email_events_id", table_name="email_events")
    op.drop_table("email_events")
    op.drop_index("ix_email_connections_user_id", table_name="email_connections")
    op.drop_index("ix_email_connections_id", table_name="email_connections")
    op.drop_table("email_connections")
