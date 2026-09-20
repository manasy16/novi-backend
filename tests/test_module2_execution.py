from types import SimpleNamespace
from uuid import uuid4

from app.graph.nodes import module2_executor
from app.graph.workflow import (
    build_module1_graph,
    route_after_module2_trigger,
)
from app.module2.schemas.input import Module2Input


def test_module2_not_triggered_routes_directly_to_output_guardrail():
    executor_calls = []

    def record_executor_call():
        executor_calls.append(True)

    destination = route_after_module2_trigger(
        {"module2_triggered": False}
    )
    if destination == "execute_module2":
        record_executor_call()

    assert destination == "output_guardrail"
    assert executor_calls == []


def test_module2_triggered_executor_uses_handoff_and_existing_db(
    monkeypatch,
):
    student_id = uuid4()
    db = object()
    state = {
        "student_id": student_id,
        "module2_triggered": True,
        "module2_trigger_reasons": ["new_project"],
    }
    module2_input = Module2Input(
        student_id=student_id,
        trigger_reasons=state["module2_trigger_reasons"],
    )
    calls = {}

    def create_input(received_state):
        calls["handoff_state"] = received_state
        return module2_input

    def run(received_input, received_db):
        calls["service_input"] = received_input
        calls["service_db"] = received_db
        return {"discovery_run_id": uuid4(), "status": "completed"}

    monkeypatch.setattr(
        module2_executor.module2_handoff_service,
        "create_input",
        create_input,
    )
    monkeypatch.setattr(module2_executor.module2_service, "run", run)

    result = module2_executor.execute_module2_node(
        state,
        SimpleNamespace(context={"db": db}),
    )

    assert route_after_module2_trigger(state) == "execute_module2"
    assert calls["handoff_state"] is state
    assert calls["service_input"] is module2_input
    assert calls["service_input"].trigger_reasons == ["new_project"]
    assert calls["service_db"] is db
    assert result["module2_result"]["status"] == "completed"


def test_module2_routes_to_output_guardrail_after_execution():
    graph = build_module1_graph().get_graph()
    edges = {(edge.source, edge.target) for edge in graph.edges}

    assert ("execute_module2", "output_guardrail") in edges
    assert ("decide_module2_trigger", "execute_module2") in edges
    assert ("decide_module2_trigger", "output_guardrail") in edges
