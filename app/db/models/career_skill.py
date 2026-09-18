import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CareerSkill(Base):
    """Associates a career with one of its required skills."""

    __tablename__ = "career_skills"
    __table_args__ = (
        CheckConstraint(
            "importance BETWEEN 1 AND 5",
            name="ck_career_skills_importance",
        ),
    )

    career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("careers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    importance: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3
    )
    required_level: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    is_core: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    career = relationship("Career")
    skill = relationship("Skill")