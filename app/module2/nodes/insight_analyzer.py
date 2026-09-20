from app.module2.graph.state import Module2State
from app.module2.services.insight_service import insight_service


def insight_analyzer_node(state: Module2State):

    profile = state.get(
        "student_profile",
        {}
    )

    insights = insight_service.analyze(
        profile
    )

    return {
        "insights": insights
    }