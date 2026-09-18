import uuid

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CareerMatchGap(Base):
    """A skill gap associated with a student's career match."""

    __tablename__ = "career_match_gaps"
    __table_args__ = (
        CheckConstraint(
            "(gap_severity IS NULL OR (gap_severity >= 0 AND gap_severity <= 1))",
            name="ck_career_match_gaps_severity",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    career_match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_skill_level: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    required_level: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    gap_severity: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    is_critical: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    career_match = relationship("CareerMatch")
    skill = relationship("Skill")