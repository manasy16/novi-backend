import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.discovery_run import DiscoveryRun


class DiscoveryRepository:
    """Persistence operations for Module 2 discovery runs."""

    @staticmethod
    def create_run(
        db: Session,
        student_id: uuid.UUID,
        trigger: str | None,
        career_dna_version: int = 1,
        thread_id: str | None = None,
    ) -> DiscoveryRun:
        """Create and flush a running discovery record."""
        discovery_run = DiscoveryRun(
            student_id=student_id,
            career_dna_version=career_dna_version,
            thread_id=thread_id,
            trigger=trigger,
            status="running",
        )

        db.add(discovery_run)
        db.flush()

        return discovery_run

    @staticmethod
    def mark_completed(
        discovery_run: DiscoveryRun,
    ) -> DiscoveryRun:
        """Mark a discovery record as completed."""
        discovery_run.status = "completed"
        discovery_run.completed_at = func.now()
        return discovery_run

    @staticmethod
    def mark_failed(
        discovery_run: DiscoveryRun,
        error_message: str,
    ) -> DiscoveryRun:
        """Mark a discovery record as failed with its execution error."""
        discovery_run.status = "failed"
        discovery_run.completed_at = func.now()
        discovery_run.error_message = error_message
        return discovery_run