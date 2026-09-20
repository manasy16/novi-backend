from app.module2.graph.state import Module2State
from app.module2.services.intelligence_service import (
    intelligence_service,
)


def intelligence_builder_node(state: Module2State):

    student_intelligence = (
        intelligence_service.build_intelligence(
            profile=state.get(
                "student_profile",
                {},
            ),
            insights=state.get(
                "insights",
                [],
            ),
            career_dna=state.get(
                "career_dna",
                {},
            ),
            career_matches=state.get(
                "career_matches",
                [],
            ),
            skill_gaps=state.get(
                "skill_gaps",
                [],
            ),
            readiness=state.get(
                "readiness",
                {},
            ),
        )
    )

    return {
        "student_intelligence": student_intelligence,
    }