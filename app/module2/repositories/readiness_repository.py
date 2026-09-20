import uuid

from sqlalchemy.orm import Session

from app.db.models.readiness import Readiness


class ReadinessRepository:
    """Persistence operations for Module 2 readiness assessments."""

    @staticmethod
    def create_readiness(
        db: Session,
        student_id: uuid.UUID,
        discovery_run_id: uuid.UUID,
        readiness_result: dict,
    ) -> Readiness:
        """Create and flush one readiness record for the current run."""
        record = Readiness(
            student_id=student_id,
            discovery_run_id=discovery_run_id,
            career_id=readiness_result.get("career_id"),
            overall_score=readiness_result.get("readiness_score"),
            skill_readiness=None,
            experience_readiness=None,
            project_readiness=None,
            career_clarity=None,
            evidence={
                "confidence": readiness_result.get("confidence"),
                "status": readiness_result.get("status"),
                "evidence": readiness_result.get("evidence", []),
                "strengths": readiness_result.get("strengths", []),
                "gaps": readiness_result.get("gaps", []),
                "critical_gaps": readiness_result.get("critical_gaps"),
                "career_name": readiness_result.get("career_name"),
            },
        )

        db.add(record)
        db.flush()

        return record