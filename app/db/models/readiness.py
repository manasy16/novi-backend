import uuid

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Readiness(Base):
    """Readiness assessment for a student and optional career."""

    __tablename__ = "readiness"
    __table_args__ = (
        CheckConstraint(
            "(overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 1))",
            name="ck_readiness_overall_score",
        ),
        CheckConstraint(
            "(skill_readiness IS NULL OR (skill_readiness >= 0 AND skill_readiness <= 1))",
            name="ck_readiness_skill_readiness",
        ),
        CheckConstraint(
            "(experience_readiness IS NULL OR (experience_readiness >= 0 AND experience_readiness <= 1))",
            name="ck_readiness_experience_readiness",
        ),
        CheckConstraint(
            "(project_readiness IS NULL OR (project_readiness >= 0 AND project_readiness <= 1))",
            name="ck_readiness_project_readiness",
        ),
        CheckConstraint(
            "(career_clarity IS NULL OR (career_clarity >= 0 AND career_clarity <= 1))",
            name="ck_readiness_career_clarity",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    discovery_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("discovery_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    career_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=True,
    )
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    skill_readiness: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_readiness: Mapped[float | None] = mapped_column(Float, nullable=True)
    project_readiness: Mapped[float | None] = mapped_column(Float, nullable=True)
    career_clarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    student = relationship("Student")
    discovery_run = relationship("DiscoveryRun")
    career = relationship("Career")