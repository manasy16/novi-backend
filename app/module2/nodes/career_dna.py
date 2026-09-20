from app.module2.graph.state import Module2State
from app.module2.services.career_dna_service import (
    career_dna_service,
)


def career_dna_node(state: Module2State):

    profile = state.get(
        "student_profile",
        {}
    )

    insights = state.get(
        "insights",
        []
    )

    career_dna = career_dna_service.build_career_dna(
        profile,
        insights,
    )

    return {
        "career_dna": career_dna
    }