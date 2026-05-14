"""add job status history

Revision ID: 0003_add_job_status_history
Revises: 0002_add_users
Create Date: 2026-05-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_add_job_status_history"
down_revision = "0002_add_users"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "job_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("old_status", sa.String(length=32), nullable=True),
        sa.Column("new_status", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False, server_default="manual"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], name="fk_job_status_history_job_id_jobs"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_job_status_history_user_id_users"),
    )
    op.create_index("ix_job_status_history_id", "job_status_history", ["id"])
    op.create_index("ix_job_status_history_job_id", "job_status_history", ["job_id"])
    op.create_index("ix_job_status_history_user_id", "job_status_history", ["user_id"])


def downgrade():
    op.drop_index("ix_job_status_history_user_id", table_name="job_status_history")
    op.drop_index("ix_job_status_history_job_id", table_name="job_status_history")
    op.drop_index("ix_job_status_history_id", table_name="job_status_history")
    op.drop_table("job_status_history")
