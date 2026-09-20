from uuid import uuid4

from app.module2.services.handoff_service import (
    module2_handoff_service,
)


def test_module2_handoff():

    student_id = uuid4()

    state = {
        "student_id": student_id,

        "relevant_memories": [
            {
                "memory_type": "project",
                "memory_key": "ml_project",
                "value": "New ML project",
            }
        ],

        "weekly_update_summary": {
            "summary": "Worked on ML project"
        },

        "weekly_new_information": [
            "Started an ML project"
        ],

        "weekly_changes": [],

        "module2_trigger_reasons": [
            "new_project"
        ],
    }

    result = module2_handoff_service.create_input(
        state
    )

    assert result.student_id == student_id

    assert len(result.relevant_memories) == 1

    assert result.trigger_reasons == [
        "new_project"
    ]

    assert result.weekly_update_summary[
        "summary"
    ] == "Worked on ML project"