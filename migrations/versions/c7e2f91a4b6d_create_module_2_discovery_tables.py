"""create module 2 discovery tables

Revision ID: c7e2f91a4b6d
Revises: 80431bc0bf5e
Create Date: 2026-09-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import UserDefinedType


# revision identifiers, used by Alembic.
revision: str = "c7e2f91a4b6d"
down_revision: Union[str, Sequence[str], None] = "80431bc0bf5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class Vector(UserDefinedType):
    """PostgreSQL vector type without requiring the pgvector package."""

    cache_ok = True

    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    def get_col_spec(self, **kwargs) -> str:
        return f"VECTOR({self.dimensions})"


def upgrade() -> None:
    """Create Module 2 discovery tables."""
    op.create_table(
        "careers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("experience_level", sa.String(length=100), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_careers_slug", "careers", ["slug"], unique=True)

    op.create_table(
        "skills",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "career_skills",
        sa.Column("career_id", sa.UUID(), nullable=False),
        sa.Column("skill_id", sa.UUID(), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=False),
        sa.Column("required_level", sa.String(length=50), nullable=True),
        sa.Column("is_core", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "importance BETWEEN 1 AND 5",
            name="ck_career_skills_importance",
        ),
        sa.ForeignKeyConstraint(
            ["career_id"], ["careers.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("career_id", "skill_id"),
    )

    op.create_table(
        "career_tags",
        sa.Column("career_id", sa.UUID(), nullable=False),
        sa.Column("tag", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["career_id"], ["careers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("career_id", "tag"),
    )

    op.create_table(
        "discovery_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("career_dna_version", sa.Integer(), nullable=True),
        sa.Column("thread_id", sa.String(length=200), nullable=True),
        sa.Column("trigger", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["student_id"], ["students.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_discovery_runs_student_id",
        "discovery_runs",
        ["student_id"],
        unique=False,
    )

    op.create_table(
        "student_skills",
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("skill_id", sa.UUID(), nullable=False),
        sa.Column("level", sa.String(length=50), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_student_skills_confidence",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"], ["students.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("student_id", "skill_id"),
    )

    op.create_table(
        "career_matches",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("discovery_run_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("career_id", sa.UUID(), nullable=False),
        sa.Column("tag_score", sa.Float(), nullable=True),
        sa.Column("semantic_score", sa.Float(), nullable=True),
        sa.Column("ai_score", sa.Float(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("why_fit", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "tag_score IS NULL OR (tag_score >= 0 AND tag_score <= 1)",
            name="ck_career_matches_tag_score",
        ),
        sa.CheckConstraint(
            "semantic_score IS NULL OR (semantic_score >= 0 AND semantic_score <= 1)",
            name="ck_career_matches_semantic_score",
        ),
        sa.CheckConstraint(
            "ai_score IS NULL OR (ai_score >= 0 AND ai_score <= 1)",
            name="ck_career_matches_ai_score",
        ),
        sa.CheckConstraint(
            "final_score IS NULL OR (final_score >= 0 AND final_score <= 1)",
            name="ck_career_matches_final_score",
        ),
        sa.ForeignKeyConstraint(
            ["discovery_run_id"], ["discovery_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["student_id"], ["students.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["career_id"], ["careers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_career_matches_discovery_run_id",
        "career_matches",
        ["discovery_run_id"],
        unique=False,
    )
    op.create_index(
        "ix_career_matches_student_id",
        "career_matches",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        "ix_career_matches_career_id",
        "career_matches",
        ["career_id"],
        unique=False,
    )

    op.create_table(
        "career_match_gaps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("career_match_id", sa.UUID(), nullable=False),
        sa.Column("skill_id", sa.UUID(), nullable=False),
        sa.Column("student_skill_level", sa.String(length=50), nullable=True),
        sa.Column("required_level", sa.String(length=50), nullable=True),
        sa.Column("gap_severity", sa.Float(), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "gap_severity IS NULL OR (gap_severity >= 0 AND gap_severity <= 1)",
            name="ck_career_match_gaps_severity",
        ),
        sa.ForeignKeyConstraint(
            ["career_match_id"], ["career_matches.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_career_match_gaps_career_match_id",
        "career_match_gaps",
        ["career_match_id"],
        unique=False,
    )

    op.create_table(
        "readiness",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("discovery_run_id", sa.UUID(), nullable=False),
        sa.Column("career_id", sa.UUID(), nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("skill_readiness", sa.Float(), nullable=True),
        sa.Column("experience_readiness", sa.Float(), nullable=True),
        sa.Column("project_readiness", sa.Float(), nullable=True),
        sa.Column("career_clarity", sa.Float(), nullable=True),
        sa.Column("evidence", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 1)",
            name="ck_readiness_overall_score",
        ),
        sa.CheckConstraint(
            "skill_readiness IS NULL OR (skill_readiness >= 0 AND skill_readiness <= 1)",
            name="ck_readiness_skill_readiness",
        ),
        sa.CheckConstraint(
            "experience_readiness IS NULL OR (experience_readiness >= 0 AND experience_readiness <= 1)",
            name="ck_readiness_experience_readiness",
        ),
        sa.CheckConstraint(
            "project_readiness IS NULL OR (project_readiness >= 0 AND project_readiness <= 1)",
            name="ck_readiness_project_readiness",
        ),
        sa.CheckConstraint(
            "career_clarity IS NULL OR (career_clarity >= 0 AND career_clarity <= 1)",
            name="ck_readiness_career_clarity",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"], ["students.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["discovery_run_id"], ["discovery_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["career_id"], ["careers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_readiness_student_id", "readiness", ["student_id"], unique=False
    )
    op.create_index(
        "ix_readiness_discovery_run_id",
        "readiness",
        ["discovery_run_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop Module 2 discovery tables."""
    op.drop_index("ix_readiness_discovery_run_id", table_name="readiness")
    op.drop_index("ix_readiness_student_id", table_name="readiness")
    op.drop_table("readiness")
    op.drop_index(
        "ix_career_match_gaps_career_match_id",
        table_name="career_match_gaps",
    )
    op.drop_table("career_match_gaps")
    op.drop_index("ix_career_matches_career_id", table_name="career_matches")
    op.drop_index("ix_career_matches_student_id", table_name="career_matches")
    op.drop_index(
        "ix_career_matches_discovery_run_id",
        table_name="career_matches",
    )
    op.drop_table("career_matches")
    op.drop_table("student_skills")
    op.drop_index(
        "ix_discovery_runs_student_id", table_name="discovery_runs"
    )
    op.drop_table("discovery_runs")
    op.drop_table("career_tags")
    op.drop_table("career_skills")
    op.drop_table("skills")
    op.drop_index("ix_careers_slug", table_name="careers")
    op.drop_table("careers")