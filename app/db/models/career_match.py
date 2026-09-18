import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CareerMatch(Base):
    """A career match produced by a discovery run."""

    __tablename__ = "career_matches"
    __table_args__ = (
        CheckConstraint(
            "(tag_score IS NULL OR (tag_score >= 0 AND tag_score <= 1))",
            name="ck_career_matches_tag_score",
        ),
        CheckConstraint(
            "(semantic_score IS NULL OR (semantic_score >= 0 AND semantic_score <= 1))",
            name="ck_career_matches_semantic_score",
        ),
        CheckConstraint(
            "(ai_score IS NULL OR (ai_score >= 0 AND ai_score <= 1))",
            name="ck_career_matches_ai_score",
        ),
        CheckConstraint(
            "(final_score IS NULL OR (final_score >= 0 AND final_score <= 1))",
            name="ck_career_matches_final_score",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    discovery_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("discovery_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    semantic_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    why_fit: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    discovery_run = relationship("DiscoveryRun")
    student = relationship("Student")
    career = relationship("Career")