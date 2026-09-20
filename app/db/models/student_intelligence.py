import uuid

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class StudentIntelligence(Base):
    """A consolidated intelligence snapshot for one discovery run."""

    __tablename__ = "student_intelligence"

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
        unique=True,
        index=True,
    )
    profile_summary: Mapped[dict] = mapped_column(JSONB, nullable=False)
    insights: Mapped[list] = mapped_column(JSONB, nullable=False)
    career_dna: Mapped[dict] = mapped_column(JSONB, nullable=False)
    career_alignment: Mapped[dict] = mapped_column(JSONB, nullable=False)
    skill_gaps: Mapped[list] = mapped_column(JSONB, nullable=False)
    readiness: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    student = relationship("Student")
    discovery_run = relationship("DiscoveryRun")