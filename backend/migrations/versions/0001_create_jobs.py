"""create jobs table

Revision ID: 0001_create_jobs
Revises:
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_create_jobs"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    job_status = postgresql.ENUM(
        "APPLIED",
        "INTERVIEW",
        "REJECTED",
        "OFFER",
        name="jobstatus",
        create_type=False,
    )
    job_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("company", sa.String(length=160), nullable=False),
        sa.Column("job_title", sa.String(length=200), nullable=False),
        sa.Column("job_url", sa.String(length=1000), nullable=False),
        sa.Column("date_applied", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("salary_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("salary_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_jobs_id", "jobs", ["id"])
    op.create_index("ix_jobs_company", "jobs", ["company"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_date_applied", "jobs", ["date_applied"])


def downgrade():
    op.drop_index("ix_jobs_date_applied", table_name="jobs")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_jobs_company", table_name="jobs")
    op.drop_index("ix_jobs_id", table_name="jobs")
    op.drop_table("jobs")
    postgresql.ENUM(name="jobstatus").drop(op.get_bind(), checkfirst=True)
