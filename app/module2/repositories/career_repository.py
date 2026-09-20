from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.career import Career
from app.db.models.career_skill import CareerSkill
from app.db.models.skill import Skill
from app.db.models.career_tag import CareerTag


class CareerRepository:

    def get_active_careers(self, db: Session):
        statement = (
            select(Career)
            .where(Career.is_active.is_(True))
        )

        return list(
            db.scalars(statement).all()
        )

    def get_all_career_skills(self, db: Session):
        statement = (
            select(CareerSkill, Skill)
            .join(
                Skill,
                Skill.id == CareerSkill.skill_id,
            )
        )

        rows = db.execute(statement).all()

        grouped = defaultdict(list)

        for career_skill, skill in rows:
            grouped[career_skill.career_id].append(
                (career_skill, skill)
            )

        return grouped

    def get_all_career_tags(self, db: Session):
        statement = select(
            CareerTag.career_id,
            CareerTag.tag,
        )

        rows = db.execute(statement).all()

        grouped = defaultdict(list)

        for career_id, tag in rows:
            grouped[career_id].append(tag)

        return grouped


career_repository = CareerRepository()