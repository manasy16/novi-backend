from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.database import SessionLocal
from app.db.models.discovery_run import DiscoveryRun
from app.db.models.student import Student
from app.db.models.student_intelligence import StudentIntelligence


def test_student_intelligence_round_trip_and_unique_discovery_run():
    student_id = uuid4()
    discovery_run_id = uuid4()
    db = SessionLocal()

    snapshot = {
        "profile_summary": {
            "total_facts": 3,
            "categories_present": ["skills", "projects"],
        },
        "insights": [{"type": "applied_learning", "confidence": 0.9}],
        "career_dna": {"technical_orientation": {"score": 0.8}},
        "career_alignment": {
            "top_careers": [{"career_id": str(uuid4()), "final_score": 0.7}]
        },
        "skill_gaps": [{"skill_name": "SQL", "gap_severity": 0.6}],
        "readiness": {"readiness_score": 0.72, "status": "moderate"},
    }

    try:
        db.add(
            Student(
                id=student_id,
                external_id=f"student-intelligence-test-{student_id}",
            )
        )
        db.add(
            DiscoveryRun(
                id=discovery_run_id,
                student_id=student_id,
                status="completed",
            )
        )
        db.commit()

        intelligence = StudentIntelligence(
            student_id=student_id,
            discovery_run_id=discovery_run_id,
            **snapshot,
        )
        db.add(intelligence)
        db.commit()

        persisted = db.get(StudentIntelligence, intelligence.id)

        assert persisted is not None
        assert persisted.student_id == student_id
        assert persisted.discovery_run_id == discovery_run_id
        assert persisted.profile_summary == snapshot["profile_summary"]
        assert persisted.insights == snapshot["insights"]
        assert persisted.career_dna == snapshot["career_dna"]
        assert persisted.career_alignment == snapshot["career_alignment"]
        assert persisted.skill_gaps == snapshot["skill_gaps"]
        assert persisted.readiness == snapshot["readiness"]

        duplicate = StudentIntelligence(
            student_id=student_id,
            discovery_run_id=discovery_run_id,
            **snapshot,
        )
        db.add(duplicate)

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()
    finally:
        db.close()
