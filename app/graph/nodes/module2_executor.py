from app.graph.state.state import State1
from app.module2.services.handoff_service import (
    module2_handoff_service,
)
from app.module2.services.module2_service import module2_service


def execute_module2_node(state: State1, runtime):
    """Execute Module 2 using the current Module 1 request session."""
    db = runtime.context["db"]
    module2_input = module2_handoff_service.create_input(state)
    result = module2_service.run(module2_input, db)

    return {
        "module2_result": result,
    }