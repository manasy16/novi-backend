from app.module2.graph.state import Module2State
from app.module2.services.profile_service import profile_service


def profile_builder_node(state: Module2State):

    memories = state.get("relevant_memories", [])

    student_profile = profile_service.build_profile(
        memories
    )

    return {
        "student_profile": student_profile
    }