from uuid import uuid4

import pytest

from app.db.database import SessionLocal
from app.db.models.career import Career
from app.db.models.career_match import CareerMatch
from app.db.models.career_match_gap import CareerMatchGap
from app.db.models.discovery_run import DiscoveryRun
from app.db.models.readiness import Readiness
from app.db.models.student import Student
from app.db.models.student_intelligence import StudentIntelligence
from app.module2.schemas.input import Module2Input
from app.module2.services.module2_service import Module2Service


class FailingGraph:
    def invoke(self, initial_state, context):
        raise RuntimeError("module2 graph failed")


class SuccessfulGraph:
    def __init__(self, career_id=None):
        self.career_id = career_id or uuid4()

    def invoke(self, initial_state, context):
        return {
            "career_matches": [
                {
                    "career_id": self.career_id,
                    "final_score": 0.5,
                }
            ],
            "student_intelligence": {
                "profile_summary": {},
                "insights": [],
                "career_dna": {},
                "career_alignment": {},
                "skill_gaps": [],
                "readiness": {},
            },
        }


class FailingCareerMatchRepository:
    def create_matches(self, db, discovery_run_id, student_id, matches):
        raise RuntimeError("career match persistence failed")


class FailingCareerMatchGapRepository:
    def create_gaps(self, db, career_matches, skill_gaps):
        raise RuntimeError("career match gap persistence failed")


class FailingReadinessRepository:
    def create_readiness(
        self,
        db,
        student_id,
        discovery_run_id,
        readiness_result,
    ):
        raise RuntimeError("readiness persistence failed")


class FailingIntelligenceRepository:
    def create_intelligence(
        self,
        db,
        student_id,
        discovery_run_id,
        student_intelligence,
    ):
        raise RuntimeError("intelligence persistence failed")


def test_failed_module2_run_is_persisted():
    student_id = uuid4()
    db = SessionLocal()

    try:
        db.add(
            Student(
                id=student_id,
                external_id=f"module2-failure-test-{student_id}",
            )
        )
        db.commit()

        service = Module2Service(graph=FailingGraph())

        with pytest.raises(RuntimeError, match="module2 graph failed"):
            service.run(
                Module2Input(
                    student_id=student_id,
                    trigger_reasons=["career_goal_changed"],
                ),
                db,
            )

        discovery_run = (
            db.query(DiscoveryRun)
            .filter(DiscoveryRun.student_id == student_id)
            .one()
        )

        assert discovery_run.status == "failed"
        assert discovery_run.completed_at is not None
        assert discovery_run.error_message == "module2 graph failed"
        assert discovery_run.trigger == "career_goal_changed"
        assert discovery_run.career_dna_version == 1
    finally:
        db.close()


def test_career_match_failure_marks_run_failed():
    student_id = uuid4()
    db = SessionLocal()

    try:
        db.add(
            Student(
                id=student_id,
                external_id=f"module2-match-failure-test-{student_id}",
            )
        )
        db.commit()

        service = Module2Service(
            graph=SuccessfulGraph(),
            career_match_repository=FailingCareerMatchRepository(),
        )

        with pytest.raises(
            RuntimeError,
            match="career match persistence failed",
        ):
            service.run(
                Module2Input(
                    student_id=student_id,
                    trigger="career_alignment",
                ),
                db,
            )

        discovery_run = (
            db.query(DiscoveryRun)
            .filter(DiscoveryRun.student_id == student_id)
            .one()
        )

        assert discovery_run.status == "failed"
        assert discovery_run.error_message == (
            "career match persistence failed"
        )
        assert (
            db.query(CareerMatch)
            .filter(CareerMatch.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
    finally:
        db.close()


def test_career_match_gap_failure_rolls_back_matches():
    student_id = uuid4()
    career_id = uuid4()
    db = SessionLocal()

    try:
        db.add_all(
            [
                Student(
                    id=student_id,
                    external_id=f"module2-gap-failure-test-{student_id}",
                ),
                Career(
                    id=career_id,
                    name="Module 2 Gap Test Career",
                    slug=f"module-2-gap-test-{career_id}",
                    is_active=True,
                ),
            ]
        )
        db.commit()

        service = Module2Service(
            graph=SuccessfulGraph(career_id),
            career_match_gap_repository=FailingCareerMatchGapRepository(),
        )

        with pytest.raises(
            RuntimeError,
            match="career match gap persistence failed",
        ):
            service.run(
                Module2Input(
                    student_id=student_id,
                    trigger="gap_analysis",
                ),
                db,
            )

        discovery_run = (
            db.query(DiscoveryRun)
            .filter(DiscoveryRun.student_id == student_id)
            .one()
        )

        assert discovery_run.status == "failed"
        assert discovery_run.error_message == (
            "career match gap persistence failed"
        )
        assert (
            db.query(CareerMatch)
            .filter(CareerMatch.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
    finally:
        db.close()


def test_readiness_failure_rolls_back_match_and_gap_rows():
    student_id = uuid4()
    career_id = uuid4()
    db = SessionLocal()

    try:
        db.add_all(
            [
                Student(
                    id=student_id,
                    external_id=f"module2-readiness-failure-test-{student_id}",
                ),
                Career(
                    id=career_id,
                    name="Module 2 Readiness Test Career",
                    slug=f"module-2-readiness-test-{career_id}",
                    is_active=True,
                ),
            ]
        )
        db.commit()

        service = Module2Service(
            graph=SuccessfulGraph(career_id),
            readiness_repository=FailingReadinessRepository(),
        )

        with pytest.raises(
            RuntimeError,
            match="readiness persistence failed",
        ):
            service.run(
                Module2Input(
                    student_id=student_id,
                    trigger="readiness_analysis",
                ),
                db,
            )

        discovery_run = (
            db.query(DiscoveryRun)
            .filter(DiscoveryRun.student_id == student_id)
            .one()
        )

        assert discovery_run.status == "failed"
        assert discovery_run.error_message == "readiness persistence failed"
        assert (
            db.query(CareerMatch)
            .filter(CareerMatch.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
        assert (
            db.query(CareerMatchGap)
            .join(
                CareerMatch,
                CareerMatch.id == CareerMatchGap.career_match_id,
            )
            .filter(CareerMatch.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
        assert (
            db.query(Readiness)
            .filter(Readiness.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
    finally:
        db.close()


def test_intelligence_failure_rolls_back_all_result_rows():
    student_id = uuid4()
    career_id = uuid4()
    db = SessionLocal()

    try:
        db.add_all(
            [
                Student(
                    id=student_id,
                    external_id=f"module2-intelligence-failure-test-{student_id}",
                ),
                Career(
                    id=career_id,
                    name="Module 2 Intelligence Test Career",
                    slug=f"module-2-intelligence-test-{career_id}",
                    is_active=True,
                ),
            ]
        )
        db.commit()

        service = Module2Service(
            graph=SuccessfulGraph(career_id),
            intelligence_repository=FailingIntelligenceRepository(),
        )

        with pytest.raises(
            RuntimeError,
            match="intelligence persistence failed",
        ):
            service.run(
                Module2Input(
                    student_id=student_id,
                    trigger="intelligence_builder",
                ),
                db,
            )

        discovery_run = (
            db.query(DiscoveryRun)
            .filter(DiscoveryRun.student_id == student_id)
            .one()
        )

        assert discovery_run.status == "failed"
        assert discovery_run.error_message == (
            "intelligence persistence failed"
        )
        assert (
            db.query(CareerMatch)
            .filter(CareerMatch.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
        assert (
            db.query(CareerMatchGap)
            .join(
                CareerMatch,
                CareerMatch.id == CareerMatchGap.career_match_id,
            )
            .filter(CareerMatch.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
        assert (
            db.query(Readiness)
            .filter(Readiness.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
        assert (
            db.query(StudentIntelligence)
            .filter(StudentIntelligence.discovery_run_id == discovery_run.id)
            .count()
            == 0
        )
    finally:
        db.close()