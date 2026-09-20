from app.graph.state.state import State1
from app.module2.schemas.input import Module2Input


class Module2HandoffService:

    @staticmethod
    def create_input(state: State1) -> Module2Input:

        return Module2Input(
            student_id=state["student_id"],

            relevant_memories=state.get(
                "relevant_memories",
                [],
            ),

            weekly_update_summary=state.get(
                "weekly_update_summary"
            ),

            weekly_new_information=state.get(
                "weekly_new_information",
                [],
            ),

            weekly_changes=state.get(
                "weekly_changes",
                [],
            ),

            trigger_reasons=state.get(
                "module2_trigger_reasons",
                [],
            ),
        )


module2_handoff_service = Module2HandoffService()