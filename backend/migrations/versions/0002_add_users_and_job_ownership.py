"""add users and job ownership

Revision ID: 0002_add_users
Revises: 0001_create_jobs
Create Date: 2026-05-11
"""
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_add_users"
down_revision = "0001_create_jobs"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    demo_user_id = uuid.uuid4()
    op.execute(
        sa.text(
            """
            INSERT INTO users (id, email, full_name, hashed_password)
            VALUES (:id, :email, :full_name, :hashed_password)
            """
        ).bindparams(
            id=str(demo_user_id),
            email="demo@example.com",
            full_name="Demo User",
            hashed_password="migration-placeholder",
        )
    )

    op.add_column("jobs", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute(sa.text("UPDATE jobs SET user_id = :user_id").bindparams(user_id=str(demo_user_id)))
    op.alter_column("jobs", "user_id", nullable=False)
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])
    op.create_foreign_key("fk_jobs_user_id_users", "jobs", "users", ["user_id"], ["id"])


def downgrade():
    op.drop_constraint("fk_jobs_user_id_users", "jobs", type_="foreignkey")
    op.drop_index("ix_jobs_user_id", table_name="jobs")
    op.drop_column("jobs", "user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
