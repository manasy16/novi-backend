import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.student_intelligence import StudentIntelligence


def _json_safe(value: Any) -> Any:
    """Convert UUID values to their JSON representation without reshaping data."""
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {
            key: _json_safe(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


class IntelligenceRepository:
    """Persistence operations for final Student Intelligence snapshots."""

    @staticmethod
    def get_latest_intelligence(
        db: Session,
        student_id: uuid.UUID,
    ) -> StudentIntelligence | None:
        """Return the latest intelligence snapshot for a student."""
        return (
            db.query(StudentIntelligence)
            .filter(StudentIntelligence.student_id == student_id)
            .order_by(StudentIntelligence.created_at.desc())
            .first()
        )

    @staticmethod
    def create_intelligence(
        db: Session,
        student_id: uuid.UUID,
        discovery_run_id: uuid.UUID,
        student_intelligence: dict,
    ) -> StudentIntelligence:
        """Create and flush the exact intelligence snapshot for a run."""
        record = StudentIntelligence(
            student_id=student_id,
            discovery_run_id=discovery_run_id,
            profile_summary=_json_safe(
                student_intelligence["profile_summary"]
            ),
            insights=_json_safe(student_intelligence["insights"]),
            career_dna=_json_safe(student_intelligence["career_dna"]),
            career_alignment=_json_safe(
                student_intelligence["career_alignment"]
            ),
            skill_gaps=_json_safe(student_intelligence["skill_gaps"]),
            readiness=_json_safe(student_intelligence["readiness"]),
        )

        db.add(record)
        db.flush()

        return record