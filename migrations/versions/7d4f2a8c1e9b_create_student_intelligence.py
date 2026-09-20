"""create student intelligence snapshots

Revision ID: 7d4f2a8c1e9b
Revises: 5b9ef9025c64
Create Date: 2026-09-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7d4f2a8c1e9b"
down_revision: Union[str, Sequence[str], None] = "5b9ef9025c64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Student Intelligence snapshot storage."""
    op.create_table(
        "student_intelligence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("discovery_run_id", sa.UUID(), nullable=False),
        sa.Column("profile_summary", postgresql.JSONB(), nullable=False),
        sa.Column("insights", postgresql.JSONB(), nullable=False),
        sa.Column("career_dna", postgresql.JSONB(), nullable=False),
        sa.Column("career_alignment", postgresql.JSONB(), nullable=False),
        sa.Column("skill_gaps", postgresql.JSONB(), nullable=False),
        sa.Column("readiness", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["student_id"], ["students.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["discovery_run_id"], ["discovery_runs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_student_intelligence_student_id",
        "student_intelligence",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        "ix_student_intelligence_discovery_run_id",
        "student_intelligence",
        ["discovery_run_id"],
        unique=True,
    )


def downgrade() -> None:
    """Drop Student Intelligence snapshot storage."""
    op.drop_index(
        "ix_student_intelligence_discovery_run_id",
        table_name="student_intelligence",
    )
    op.drop_index(
        "ix_student_intelligence_student_id",
        table_name="student_intelligence",
    )
    op.drop_table("student_intelligence")