from app.graph.state.state import State1
from app.services.onboarding_service import (
    onboarding_service,
)


def onboarding_analyzer_node(
    state: State1,
) -> dict:
    """
    Analyze currently known student memories and determine
    onboarding progress.
    """

    relevant_memories = (
        state.get("relevant_memories")
        or []
    )

    analysis = (
        onboarding_service.analyze_profile(
            memories=relevant_memories
        )
    )

    onboarding_status = (
        "completed"
        if analysis["onboarding_complete"]
        else "in_progress"
    )

    result = {
        "onboarding_profile":
            analysis["profile"],

        "known_categories":
            analysis["known_categories"],

        "completed_categories":
            analysis["completed_categories"],

        "missing_categories":
            analysis["missing_categories"],

        "completion_percentage":
            analysis["completion_percentage"],

        "onboarding_status":
            onboarding_status,
    }

    return result