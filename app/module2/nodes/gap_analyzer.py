from app.module2.graph.state import Module2State
from app.module2.services.skill_gap_service import (
    skill_gap_service,
)


def gap_analyzer_node(state: Module2State):

    profile = state.get(
        "student_profile",
        {},
    )

    career_matches = state.get(
        "career_matches",
        [],
    )

    skill_gaps = skill_gap_service.analyze_gaps(
        profile,
        career_matches,
    )

    return {
        "skill_gaps": skill_gaps
    }