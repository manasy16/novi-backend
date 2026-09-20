import uuid

from sqlalchemy.orm import Session

from app.db.models.career_match import CareerMatch


class CareerMatchRepository:
    """Persistence operations for career matches from one discovery run."""

    @staticmethod
    def create_matches(
        db: Session,
        discovery_run_id: uuid.UUID,
        student_id: uuid.UUID,
        matches: list[dict],
    ) -> list[CareerMatch]:
        """Bulk-create one persisted match for each alignment result."""
        career_matches = [
            CareerMatch(
                discovery_run_id=discovery_run_id,
                student_id=student_id,
                career_id=match["career_id"],
                tag_score=None,
                semantic_score=None,
                ai_score=None,
                final_score=match.get("final_score"),
                rank=rank,
                why_fit={
                    "matched_skills": match.get("matched_skills", []),
                    "required_skills": match.get("required_skills", []),
                    "skill_score": match.get("skill_score"),
                    "goal_score": match.get("goal_score"),
                    "tags": match.get("tags", []),
                },
            )
            for rank, match in enumerate(matches, start=1)
        ]

        db.add_all(career_matches)
        db.flush()

        return career_matches