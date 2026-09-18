from app.graph.state.state import State1
from app.services.guardrail_service import guardrail_service


def output_guardrail_node(state: State1) -> dict:
    """
    Validate NOVI's generated response before returning
    it to the user.
    """

    assistant_response = state.get(
        "assistant_response",
        "",
    )

    result = guardrail_service.check_output(
        assistant_response
    )

    return {
        "assistant_response": result[
            "response"
        ],
        "output_guardrail_allowed": result[
            "allowed"
        ],
        "output_guardrail_reason": result[
            "reason"
        ],
    }