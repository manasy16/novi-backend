from app.module2.graph.state import Module2State
from app.module2.repositories.career_repository import career_repository
from app.module2.services.career_matching_service import (
    career_matching_service,
)


def career_alignment_node(state: Module2State, runtime):
    db = runtime.context["db"]

    profile = state.get("student_profile", {})
    career_dna = state.get("career_dna", {})

    # Load all data in bulk
    career_list = career_repository.get_active_careers(db)
    career_skills = career_repository.get_all_career_skills(db)
    career_tags = career_repository.get_all_career_tags(db)

    careers = []

    for career in career_list:
        careers.append({
            "career": career,
            "skills": career_skills.get(career.id, []),
            "tags": career_tags.get(career.id, []),
        })

    matches = career_matching_service.match_careers(
        profile,
        career_dna,
        careers,
    )

    return {
        "career_matches": matches,
    }