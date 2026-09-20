from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.graph.state.state import State1

from app.graph.nodes.input_guardrail import (
    input_guardrail_node,
)

from app.graph.nodes.output_guardrail import (
    output_guardrail_node,
)

from app.graph.nodes.context_loader import (
    load_context,
)

from app.graph.nodes.onboarding_analyzer import (
    onboarding_analyzer_node,
)

from app.graph.nodes.conversation_node import (
    conversation_node,
)

from app.graph.nodes.memory_extractor import (
    memory_extractor_node,
)

from app.graph.nodes.memory_updater import (
    memory_updater_node,
)

from app.graph.nodes.context_refresher import (
    refresh_context,
)

from app.graph.nodes.module2_trigger import (
    decide_module2_trigger,
)
from app.graph.nodes.module2_executor import (
    execute_module2_node,
)


class Module1Context:

    def __init__(self, db):
        self.db = db


def guardrail_response_node(
    state: State1
) -> dict:

    return {
        "assistant_response": state.get(
            "guardrail_response",
            (
                "Let's keep our conversation focused "
                "on your education, learning, skills, "
                "and career development."
            ),
        )
    }


def route_after_input_guardrail(
    state: State1
):

    if state.get(
        "input_guardrail_allowed",
        False,
    ):

        return "load_context"

    return "guardrail_response"


def route_after_module2_trigger(state: State1):
    if state.get("module2_triggered", False):
        return "execute_module2"

    return "output_guardrail"


def build_module1_graph():

    workflow = StateGraph(
        State1,
        context_schema=Module1Context,
    )

    # -------------------------------------------------
    # GUARDRAILS
    # -------------------------------------------------

    workflow.add_node(
        "input_guardrail",
        input_guardrail_node,
    )

    workflow.add_node(
        "guardrail_response",
        guardrail_response_node,
    )

    workflow.add_node(
        "output_guardrail",
        output_guardrail_node,
    )

    # -------------------------------------------------
    # MODULE 1 NODES
    # -------------------------------------------------

    workflow.add_node(
        "load_context",
        load_context,
    )

    workflow.add_node(
        "analyze_onboarding_initial",
        onboarding_analyzer_node,
    )

    workflow.add_node(
        "conversation",
        conversation_node,
    )

    workflow.add_node(
        "extract_memory",
        memory_extractor_node,
    )

    workflow.add_node(
        "update_memory",
        memory_updater_node,
    )

    workflow.add_node(
        "refresh_context",
        refresh_context,
    )

    workflow.add_node(
        "analyze_onboarding_final",
        onboarding_analyzer_node,
    )

    # -------------------------------------------------
    # MODULE 2 TRIGGER DECISION
    # -------------------------------------------------

    workflow.add_node(
        "decide_module2_trigger",
        decide_module2_trigger,
    )

    workflow.add_node(
        "execute_module2",
        execute_module2_node,
    )

    # -------------------------------------------------
    # START
    # -------------------------------------------------

    workflow.add_edge(
        START,
        "input_guardrail",
    )

    # -------------------------------------------------
    # INPUT GUARDRAIL ROUTING
    # -------------------------------------------------

    workflow.add_conditional_edges(
        "input_guardrail",
        route_after_input_guardrail,
        {
            "load_context": "load_context",
            "guardrail_response": "guardrail_response",
        },
    )

    # -------------------------------------------------
    # BLOCKED INPUT
    # -------------------------------------------------

    workflow.add_edge(
        "guardrail_response",
        "output_guardrail",
    )

    # -------------------------------------------------
    # MODULE 1 FLOW
    # -------------------------------------------------

    workflow.add_edge(
        "load_context",
        "analyze_onboarding_initial",
    )

    workflow.add_edge(
        "analyze_onboarding_initial",
        "conversation",
    )

    workflow.add_edge(
        "conversation",
        "extract_memory",
    )

    workflow.add_edge(
        "extract_memory",
        "update_memory",
    )

    workflow.add_edge(
        "update_memory",
        "refresh_context",
    )

    workflow.add_edge(
        "refresh_context",
        "analyze_onboarding_final",
    )

    # -------------------------------------------------
    # MODULE 2 TRIGGER DECISION
    # -------------------------------------------------

    workflow.add_edge(
        "analyze_onboarding_final",
        "decide_module2_trigger",
    )

    # -------------------------------------------------
    # OUTPUT GUARDRAIL
    # -------------------------------------------------

    workflow.add_conditional_edges(
        "decide_module2_trigger",
        route_after_module2_trigger,
        {
            "execute_module2": "execute_module2",
            "output_guardrail": "output_guardrail",
        },
    )

    workflow.add_edge(
        "execute_module2",
        "output_guardrail",
    )

    # -------------------------------------------------
    # FINAL
    # -------------------------------------------------

    workflow.add_edge(
        "output_guardrail",
        END,
    )

    return workflow.compile()


module1_graph = build_module1_graph()