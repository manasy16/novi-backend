import json
from uuid import uuid4

from app.db.database import SessionLocal
from app.db.models.career_match import CareerMatch
from app.db.models.career_match_gap import CareerMatchGap
from app.db.models.discovery_run import DiscoveryRun
from app.db.models.readiness import Readiness
from app.db.models.skill import Skill
from app.db.models.student_intelligence import StudentIntelligence
from app.db.models.student import Student
from app.module2.schemas.input import Module2Input
from app.module2.services.module2_service import module2_service


def json_safe(value):
    return json.loads(json.dumps(value, default=str))


def test_module2_graph():

    student_id = uuid4()

    module2_input = Module2Input(
        student_id=student_id,

        relevant_memories=[
            {
                "memory_type": "project",
                "memory_key": "ml_project",
                "value": "Student started an ML project",
                "normalized_value": "machine learning project",
                "confidence": 0.9,
                "importance": 4,
            },
            {
                "memory_type": "skill",
                "memory_key": "python",
                "value": "Student knows Python",
                "normalized_value": "python",
                "confidence": 0.95,
                "importance": 5,
            },
            {
                "memory_type": "career_goal",
                "memory_key": "ai_engineer",
                "value": "Student wants to become an AI Engineer",
                "normalized_value": "AI Engineer",
                "confidence": 0.9,
                "importance": 5,
            },
        ],

        trigger_reasons=[
            "new_project"
        ],
    )

    db = SessionLocal()

    try:

        db.add(
            Student(
                id=student_id,
                external_id=f"module2-test-{student_id}",
            )
        )
        db.commit()

        result = module2_service.run(
            module2_input,
            db,
        )

        discovery_runs = (
            db.query(DiscoveryRun)
            .filter(DiscoveryRun.student_id == student_id)
            .all()
        )
        persisted_matches = (
            db.query(CareerMatch)
            .filter(CareerMatch.discovery_run_id == result["discovery_run_id"])
            .order_by(CareerMatch.rank.asc())
            .all()
        )
        persisted_gaps = (
            db.query(CareerMatchGap, Skill)
            .join(Skill, Skill.id == CareerMatchGap.skill_id)
            .join(
                CareerMatch,
                CareerMatch.id == CareerMatchGap.career_match_id,
            )
            .filter(CareerMatch.discovery_run_id == result["discovery_run_id"])
            .all()
        )
        persisted_readiness = (
            db.query(Readiness)
            .filter(
                Readiness.discovery_run_id == result["discovery_run_id"]
            )
            .all()
        )
        persisted_intelligence = (
            db.query(StudentIntelligence)
            .filter(
                StudentIntelligence.discovery_run_id
                == result["discovery_run_id"]
            )
            .all()
        )

    finally:

        db.close()

    # -----------------------------------------
    # 1. Basic state
    # -----------------------------------------

    assert result["student_id"] == student_id
    assert result["discovery_run_id"]
    assert result["student_intelligence_id"]
    assert result["status"] == "completed"
    assert len(discovery_runs) == 1
    assert discovery_runs[0].id == result["discovery_run_id"]
    assert discovery_runs[0].status == "completed"
    assert discovery_runs[0].completed_at is not None
    assert discovery_runs[0].trigger == "new_project"
    assert discovery_runs[0].career_dna_version == 1

    # -----------------------------------------
    # 2. Profile Builder
    # -----------------------------------------

    assert "student_profile" in result

    profile = result["student_profile"]

    assert len(profile["projects"]) == 1
    assert len(profile["skills"]) == 1
    assert len(profile["career_goals"]) == 1

    assert profile["total_facts"] == 3

    # -----------------------------------------
    # 3. Insight Analyzer
    # -----------------------------------------

    assert "insights" in result

    assert len(result["insights"]) >= 1

    insight_types = [
        insight["type"]
        for insight in result["insights"]
    ]

    assert "career_direction" in insight_types
    assert "applied_learning" in insight_types

    # -----------------------------------------
    # 4. Career DNA
    # -----------------------------------------

    assert "career_dna" in result

    career_dna = result["career_dna"]

    assert "technical_orientation" in career_dna
    assert "analytical_orientation" in career_dna
    assert "career_clarity" in career_dna
    assert "learning_orientation" in career_dna

    technical = career_dna["technical_orientation"]

    assert "score" in technical
    assert "confidence" in technical
    assert "evidence" in technical

    assert 0 <= technical["score"] <= 1
    assert 0 <= technical["confidence"] <= 1

    assert len(technical["evidence"]) > 0

    # -----------------------------------------
    # 5. Career Alignment
    # -----------------------------------------

    assert "career_matches" in result

    career_matches = result["career_matches"]

    assert len(career_matches) > 0

    # Every returned match should contain
    # the basic alignment information.
    first_match = career_matches[0]

    assert "career_id" in first_match
    assert "career_name" in first_match
    assert "skill_score" in first_match
    assert "goal_score" in first_match
    assert "final_score" in first_match

    assert 0 <= first_match["skill_score"] <= 1
    assert 0 <= first_match["goal_score"] <= 1
    assert 0 <= first_match["final_score"] <= 1

    # -----------------------------------------
    # 6. Ranking
    # -----------------------------------------

    scores = [
        match["final_score"]
        for match in career_matches
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )

    assert len(persisted_matches) == len(career_matches)
    assert [match.rank for match in persisted_matches] == list(
        range(1, len(persisted_matches) + 1)
    )

    for persisted_match, output_match in zip(
        persisted_matches,
        career_matches,
    ):
        assert persisted_match.discovery_run_id == result["discovery_run_id"]
        assert persisted_match.student_id == student_id
        assert persisted_match.career_id == output_match["career_id"]
        assert persisted_match.final_score == output_match["final_score"]
        assert persisted_match.tag_score is None
        assert persisted_match.semantic_score is None
        assert persisted_match.ai_score is None
        assert persisted_match.why_fit == {
            "matched_skills": output_match["matched_skills"],
            "required_skills": output_match["required_skills"],
            "skill_score": output_match["skill_score"],
            "goal_score": output_match["goal_score"],
            "tags": output_match["tags"],
        }

    # -----------------------------------------
# 7. Gap Analysis
# -----------------------------------------

    assert "skill_gaps" in result

    skill_gaps = result["skill_gaps"]

    assert isinstance(
    skill_gaps,
    list,
)

    for gap in skill_gaps:
        assert "required_level" in gap
        assert "importance" in gap
        assert "is_core" in gap
        assert "gap_severity" in gap
        assert "is_critical" in gap

        assert gap["student_skill_level"] is None
        assert 1 <= gap["importance"] <= 5
        assert 0 <= gap["gap_severity"] <= 1
        assert isinstance(gap["is_core"], bool)
        assert isinstance(gap["is_critical"], bool)

    persisted_matches_by_career = {
        match.career_id: match
        for match in persisted_matches
    }
    graph_matches_by_career = {
        match["career_id"]: match
        for match in career_matches
    }

    assert len(persisted_gaps) == len(skill_gaps)
    for persisted_gap, skill in persisted_gaps:
        matching_graph_gaps = [
            gap
            for gap in skill_gaps
            if gap["career_id"]
            == next(
                career_id
                for career_id, match in persisted_matches_by_career.items()
                if match.id == persisted_gap.career_match_id
            )
            and gap["skill_name"].lower() == skill.name.lower()
        ]
        assert len(matching_graph_gaps) == 1
        graph_gap = matching_graph_gaps[0]
        career_id = next(
            career_id
            for career_id, match in persisted_matches_by_career.items()
            if match.id == persisted_gap.career_match_id
        )
        assert persisted_matches_by_career[career_id].discovery_run_id == (
            result["discovery_run_id"]
        )
        assert skill.name.lower() not in {
            matched_skill.lower()
            for matched_skill in graph_matches_by_career[career_id][
                "matched_skills"
            ]
        }
        assert persisted_gap.student_skill_level == (
            graph_gap["student_skill_level"]
        )
        assert persisted_gap.required_level == graph_gap["required_level"]
        assert persisted_gap.gap_severity == graph_gap["gap_severity"]
        assert persisted_gap.is_critical == graph_gap["is_critical"]


    assert "readiness" in result

    readiness = result["readiness"]

    assert len(persisted_readiness) == 1
    persisted_readiness_record = persisted_readiness[0]
    assert persisted_readiness_record.discovery_run_id == (
        result["discovery_run_id"]
    )
    assert persisted_readiness_record.student_id == student_id
    assert persisted_readiness_record.career_id == readiness["career_id"]
    assert persisted_readiness_record.overall_score == (
        readiness["readiness_score"]
    )
    assert persisted_readiness_record.evidence == {
        "confidence": readiness["confidence"],
        "status": readiness["status"],
        "evidence": readiness["evidence"],
        "strengths": readiness["strengths"],
        "gaps": readiness["gaps"],
        "critical_gaps": readiness["critical_gaps"],
        "career_name": readiness["career_name"],
    }

    assert "readiness_score" in readiness
    assert "confidence" in readiness
    assert "status" in readiness
    assert "evidence" in readiness
    assert "strengths" in readiness
    assert "gaps" in readiness

    assert 0 <= readiness["readiness_score"] <= 1
    assert 0 <= readiness["confidence"] <= 1

    assert "student_intelligence" in result

    intelligence = result["student_intelligence"]

    assert len(persisted_intelligence) == 1
    intelligence_record = persisted_intelligence[0]
    assert intelligence_record.id == result["student_intelligence_id"]
    assert intelligence_record.student_id == student_id
    assert intelligence_record.discovery_run_id == result["discovery_run_id"]
    assert intelligence_record.profile_summary == json_safe(
        intelligence["profile_summary"]
    )
    assert intelligence_record.insights == json_safe(
        intelligence["insights"]
    )
    assert intelligence_record.career_dna == json_safe(
        intelligence["career_dna"]
    )
    assert intelligence_record.career_alignment == json_safe(
        intelligence["career_alignment"]
    )
    assert intelligence_record.skill_gaps == json_safe(
        intelligence["skill_gaps"]
    )
    assert intelligence_record.readiness == json_safe(
        intelligence["readiness"]
    )

    assert "profile_summary" in intelligence
    assert "insights" in intelligence
    assert "career_dna" in intelligence
    assert "career_alignment" in intelligence
    assert "skill_gaps" in intelligence
    assert "readiness" in intelligence