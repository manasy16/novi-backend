from langgraph.graph import StateGraph, START, END

from app.graph.state.state import State1

from app.graph.nodes.context_loader import load_context
from app.graph.nodes.weekly_conversation import weekly_conversation_node
from app.graph.nodes.memory_extractor import memory_extractor_node
from app.graph.nodes.memory_updater import memory_updater_node
from app.graph.nodes.context_refresher import refresh_context


def build_weekly_graph():

    workflow = StateGraph(State1)

    # ---------------------------------------------------------
    # NODES
    # ---------------------------------------------------------

    workflow.add_node(
        "load_context",
        load_context
    )

    workflow.add_node(
        "weekly_conversation",
        weekly_conversation_node
    )

    workflow.add_node(
        "extract_memory",
        memory_extractor_node
    )

    workflow.add_node(
        "update_memory",
        memory_updater_node
    )

    workflow.add_node(
        "refresh_context",
        refresh_context
    )

    # ---------------------------------------------------------
    # FLOW
    # ---------------------------------------------------------

    workflow.add_edge(
        START,
        "load_context"
    )

    workflow.add_edge(
        "load_context",
        "weekly_conversation"
    )

    workflow.add_edge(
        "weekly_conversation",
        "extract_memory"
    )

    workflow.add_edge(
        "extract_memory",
        "update_memory"
    )

    workflow.add_edge(
        "update_memory",
        "refresh_context"
    )

    workflow.add_edge(
        "refresh_context",
        END
    )

    return workflow.compile()


weekly_graph = build_weekly_graph()