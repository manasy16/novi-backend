from langgraph.graph import StateGraph, START, END

from app.module2.graph.state import Module2State

from app.module2.nodes.profile_builder import (
    profile_builder_node,
)

from app.module2.nodes.insight_analyzer import (
    insight_analyzer_node,
)

from app.module2.nodes.career_dna import (
    career_dna_node,
)

from app.module2.nodes.career_alignment import (
    career_alignment_node,
)

from app.module2.nodes.gap_analyzer import (
    gap_analyzer_node,
)

from app.module2.nodes.readiness_analyzer import (
    readiness_analyzer_node,
)

from app.module2.nodes.intelligence_builder import (
    intelligence_builder_node,
)


class Module2Context:

    def __init__(self, db):
        self.db = db


def build_module2_graph():

    workflow = StateGraph(
        Module2State,
        context_schema=Module2Context,
    )

    # -------------------------
    # Nodes
    # -------------------------

    workflow.add_node(
        "profile_builder",
        profile_builder_node,
    )

    workflow.add_node(
        "insight_analyzer",
        insight_analyzer_node,
    )

    workflow.add_node(
        "career_dna",
        career_dna_node,
    )

    workflow.add_node(
        "career_alignment",
        career_alignment_node,
    )

    workflow.add_node(
        "gap_analyzer",
        gap_analyzer_node,
    )

    workflow.add_node(
        "readiness_analyzer",
        readiness_analyzer_node,
    )

    workflow.add_node(
        "intelligence_builder",
        intelligence_builder_node,
    )

    # -------------------------
    # Edges
    # -------------------------

    workflow.add_edge(
        START,
        "profile_builder",
    )

    workflow.add_edge(
        "profile_builder",
        "insight_analyzer",
    )

    workflow.add_edge(
        "insight_analyzer",
        "career_dna",
    )

    workflow.add_edge(
        "career_dna",
        "career_alignment",
    )

    workflow.add_edge(
        "career_alignment",
        "gap_analyzer",
    )

    workflow.add_edge(
        "gap_analyzer",
        "readiness_analyzer",
    )

    workflow.add_edge(
        "readiness_analyzer",
        "intelligence_builder",
    )

    workflow.add_edge(
        "intelligence_builder",
        END,
    )

    return workflow.compile()


module2_graph = build_module2_graph()