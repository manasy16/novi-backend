"""State definitions for the Module 2 discovery intelligence graph."""

from typing import Any, Optional, TypedDict
from uuid import UUID


class Module2State(TypedDict):
    """Data passed between Module 2 pipeline stages."""

    student_id: Optional[UUID]
    external_student_id: Optional[str]
    relevant_memories: Optional[Any]
    weekly_update_summary: Optional[Any]
    weekly_new_information: Optional[Any]
    weekly_changes: Optional[Any]
    student_profile: Optional[Any]
    insights: Optional[Any]
    career_dna: Optional[Any]
    previous_career_dna: Optional[Any]
    career_dna_changes: Optional[Any]
    career_matches: Optional[Any]
    skill_gaps: Optional[Any]
    readiness: Optional[Any]
    student_intelligence: Optional[Any]
    discovery_run_id: Optional[UUID]
    trigger: Optional[str]
    status: Optional[str]
    error_message: Optional[str]