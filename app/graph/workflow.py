from langgraph.graph import StateGraph, START, END

from app.graph.state.state import State1

from app.graph.nodes.context_loader import load_context
from app.graph.nodes.onboarding_analyzer import onboarding_analyzer_node
from app.graph.nodes.conversation_node import conversation_node
from app.graph.nodes.memory_extractor import memory_extractor_node
from app.graph.nodes.memory_updater import memory_updater_node
from app.graph.nodes.context_refresher import refresh_context


def build_module1_graph():

    workflow = StateGraph(State1)

    # -------------------------------------------------
    # ADD NODES
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
    # DEFINE FLOW
    # -------------------------------------------------

    workflow.add_edge(
        START,
        "load_context",
    )

    # Initial onboarding analysis
    workflow.add_edge(
        "load_context",
        "analyze_onboarding_initial",
    )

    # Generate exactly ONE assistant response
    workflow.add_edge(
        "analyze_onboarding_initial",
        "conversation",
    )

    # Extract memories from THIS user message
    workflow.add_edge(
        "conversation",
        "extract_memory",
    )

    # Save/update memories
    workflow.add_edge(
        "extract_memory",
        "update_memory",
    )

    # Reload updated memories
    workflow.add_edge(
        "update_memory",
        "refresh_context",
    )

    # Calculate final onboarding status
    workflow.add_edge(
        "refresh_context",
        "analyze_onboarding_final",
    )

    # END THE TURN
    workflow.add_edge(
        "analyze_onboarding_final",
        END,
    )

    return workflow.compile()


module1_graph = build_module1_graph()