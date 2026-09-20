from app.module2.graph.state import Module2State
from app.module2.services.readiness_service import readiness_service


def readiness_analyzer_node(state: Module2State):

    career_matches = state.get(
        "career_matches",
        [],
    )

    skill_gaps = state.get(
        "skill_gaps",
        [],
    )

    career_dna = state.get(
        "career_dna",
        {},
    )

    readiness = readiness_service.calculate_readiness(
        career_matches=career_matches,
        skill_gaps=skill_gaps,
        career_dna=career_dna,
    )

    return {
        "readiness": readiness,
    }