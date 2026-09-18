from app.graph.state.state import State1
from app.services.guardrail_service import guardrail_service


def input_guardrail_node(state: State1) -> dict:
    """
    Validate the incoming student message before it
    reaches conversation or memory extraction.
    """

    user_message = state.get(
        "user_message",
        "",
    )

    result = guardrail_service.check_input(
        user_message
    )

    return {
        "input_guardrail_allowed": result[
            "allowed"
        ],
        "input_guardrail_category": result[
            "category"
        ],
        "input_guardrail_reason": result[
            "reason"
        ],
        "guardrail_response": result[
            "response"
        ],
    }