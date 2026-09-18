from app.graph.state.state import State1
from app.services.onboarding_service import (
    onboarding_service,
)


from app.graph.state.state import State1
from app.services.onboarding_service import onboarding_service


def onboarding_analyzer_node(state: State1):
    relevant_memories = state.get("relevant_memories") or []

    analysis = onboarding_service.analyze_profile(
        memories=relevant_memories
    )

    if analysis["onboarding_complete"]:
        onboarding_status = "completed"
        next_onboarding_focus = None

    else:
        onboarding_status = "in_progress"

        completed_categories = set(
            analysis["completed_categories"]
        )

        # -------------------------------------------------
        # BROAD FOUNDATIONAL FOCUS
        # -------------------------------------------------
        #
        # This is intentionally deterministic.
        # The LLM should NOT decide the onboarding strategy.
        #
        # We first make sure the five foundational areas
        # are covered broadly.
        # -------------------------------------------------

        foundational_priority = [
            "education",
            "interest",
            "skill",
            "career_goal",
            "learning_preference",
        ]

        next_onboarding_focus = None

        for category in foundational_priority:

            if category not in completed_categories:
                next_onboarding_focus = category
                break

    return {
        "onboarding_profile": analysis["profile"],
        "known_categories": analysis["known_categories"],
        "completed_categories": analysis["completed_categories"],
        "missing_categories": analysis["missing_categories"],
        "completion_percentage": analysis["completion_percentage"],
        "onboarding_status": onboarding_status,
        "next_onboarding_focus": next_onboarding_focus,
    }