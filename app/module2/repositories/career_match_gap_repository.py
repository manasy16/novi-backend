from collections.abc import Sequence
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.career_match import CareerMatch
from app.db.models.career_match_gap import CareerMatchGap
from app.db.models.skill import Skill


class CareerMatchGapRepository:
    """Persistence operations for gaps belonging to career matches."""

    @staticmethod
    def create_gaps(
        db: Session,
        career_matches: Sequence[CareerMatch],
        skill_gaps: list[dict],
    ) -> list[CareerMatchGap]:
        """Bulk-create gaps after resolving all required Skill records."""
        matches_by_career_id = {
            career_match.career_id: career_match
            for career_match in career_matches
        }

        skill_names = {
            gap["skill_name"].strip().lower()
            for gap in skill_gaps
        }

        skills_by_name = {}
        if skill_names:
            statement = select(Skill).where(
                func.lower(Skill.name).in_(skill_names)
            )
            skills_by_name = {
                skill.name.lower(): skill
                for skill in db.scalars(statement).all()
            }

        missing_skill_names = skill_names - set(skills_by_name)
        if missing_skill_names:
            missing = ", ".join(sorted(missing_skill_names))
            raise ValueError(
                f"No Skill record found for gap skill(s): {missing}"
            )

        career_match_gaps = []
        for gap in skill_gaps:
            career_match = matches_by_career_id.get(gap["career_id"])
            if career_match is None:
                raise ValueError(
                    "No persisted CareerMatch found for gap career "
                    f"{gap['career_id']}"
                )

            skill = skills_by_name[gap["skill_name"].strip().lower()]
            career_match_gaps.append(
                CareerMatchGap(
                    career_match_id=career_match.id,
                    skill_id=skill.id,
                    student_skill_level=gap.get("student_skill_level"),
                    required_level=gap.get("required_level"),
                    gap_severity=gap.get("gap_severity"),
                    is_critical=gap.get("is_critical", False),
                )
            )

        db.add_all(career_match_gaps)
        db.flush()

        return career_match_gaps