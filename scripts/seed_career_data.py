import json
from pathlib import Path

import pandas as pd
from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models.career import Career
from app.db.models.skill import Skill
from app.db.models.career_skill import CareerSkill
from app.db.models.career_tag import CareerTag


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def seed_careers(db):
    df = pd.read_csv(
        DATA_DIR / "careers.csv"
    )

    existing = {
        career.slug: career
        for career in db.scalars(
            select(Career)
        ).all()
    }

    created = 0

    for _, row in df.iterrows():

        slug = row["slug"]

        if slug in existing:
            continue

        metadata = row["metadata_json"]

        if pd.isna(metadata):
            metadata = {}
        else:
            try:
                metadata = json.loads(metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = {}

        career = Career(
            name=row["name"],
            slug=slug,
            description=row["description"],
            category=row["category"],
            industry=row["industry"],
            experience_level=row["experience_level"],
            metadata_json=metadata,
            is_active=True,
        )

        db.add(career)
        existing[slug] = career
        created += 1

    db.flush()

    print(
        f"Careers: created {created}, "
        f"total {len(existing)}"
    )

    return existing


def seed_skills(db):
    df = pd.read_csv(
        DATA_DIR / "skills.csv"
    )

    existing = {
        skill.slug: skill
        for skill in db.scalars(
            select(Skill)
        ).all()
    }

    created = 0

    for _, row in df.iterrows():

        slug = row["skill_slug"]

        if slug in existing:
            continue

        skill = Skill(
            name=row["skill_name"],
            slug=slug,
            category=row["skill_category"],
            description=row["skill_description"],
        )

        db.add(skill)
        existing[slug] = skill
        created += 1

    db.flush()

    print(
        f"Skills: created {created}, "
        f"total {len(existing)}"
    )

    return existing


def seed_career_skills(
    db,
    careers,
    skills,
):
    df = pd.read_csv(
        DATA_DIR / "career_skills.csv"
    )

    existing = {
        (
            item.career_id,
            item.skill_id,
        )
        for item in db.scalars(
            select(CareerSkill)
        ).all()
    }

    created = 0

    for _, row in df.iterrows():

        career_slug = row["career_slug"]
        skill_slug = row["skill_slug"]

        career = careers.get(career_slug)
        skill = skills.get(skill_slug)

        if career is None:
            print(
                f"WARNING: career not found: "
                f"{career_slug}"
            )
            continue

        if skill is None:
            print(
                f"WARNING: skill not found: "
                f"{skill_slug}"
            )
            continue

        key = (
            career.id,
            skill.id,
        )

        if key in existing:
            continue

        item = CareerSkill(
            career_id=career.id,
            skill_id=skill.id,
            importance=int(row["importance"]),
            required_level=row["required_level"],
            is_core=bool(row["is_core"]),
        )

        db.add(item)
        existing.add(key)
        created += 1

    db.flush()

    print(
        f"Career skills: created {created}"
    )


def seed_career_tags(
    db,
    careers,
):
    df = pd.read_csv(
        DATA_DIR / "career_tags.csv"
    )

    existing = {
        (
            item.career_id,
            item.tag,
        )
        for item in db.scalars(
            select(CareerTag)
        ).all()
    }

    created = 0

    for _, row in df.iterrows():

        career_slug = row["career_slug"]
        tag = row["tag"]

        career = careers.get(career_slug)

        if career is None:
            print(
                f"WARNING: career not found: "
                f"{career_slug}"
            )
            continue

        key = (
            career.id,
            tag,
        )

        if key in existing:
            continue

        item = CareerTag(
            career_id=career.id,
            tag=tag,
        )

        db.add(item)
        existing.add(key)
        created += 1

    db.flush()

    print(
        f"Career tags: created {created}"
    )


def main():

    db = SessionLocal()

    try:

        print("Starting career data seed...")
        print(f"Data directory: {DATA_DIR}")

        careers = seed_careers(db)

        skills = seed_skills(db)

        seed_career_skills(
            db,
            careers,
            skills,
        )

        seed_career_tags(
            db,
            careers,
        )

        db.commit()

        print()
        print("Career data seed completed successfully.")

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()