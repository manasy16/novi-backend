"""Response schemas for the Module 2 API."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StudentIntelligenceResponse(BaseModel):
    """A persisted Student Intelligence snapshot."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    discovery_run_id: UUID
    profile_summary: dict[str, Any]
    insights: list[Any]
    career_dna: dict[str, Any]
    career_alignment: dict[str, Any]
    skill_gaps: list[Any]
    readiness: dict[str, Any]
    created_at: datetime