from app.graph.nodes.module2_trigger import decide_module2_trigger


def test_no_trigger_for_normal_skill():

    state = {
        "extracted_memories": [
            {
                "memory_type": "skill",
                "memory_key": "linked_lists",
                "value": "Linked Lists",
            }
        ],
        "memory_updates": [
            {
                "action": "created",
                "memory_type": "skill",
                "memory_key": "linked_lists",
            }
        ],
    }

    result = decide_module2_trigger(state)

    assert result["module2_triggered"] is False
    assert result["module2_trigger_reasons"] == []


def test_trigger_for_new_project():

    state = {
        "extracted_memories": [
            {
                "memory_type": "project",
                "memory_key": "ml_project",
                "value": "New ML project",
            }
        ],
        "memory_updates": [
            {
                "action": "created",
                "memory_type": "project",
                "memory_key": "ml_project",
            }
        ],
    }

    result = decide_module2_trigger(state)

    assert result["module2_triggered"] is True
    assert "new_project" in result["module2_trigger_reasons"]


def test_trigger_for_career_goal_change():

    state = {
        "extracted_memories": [
            {
                "memory_type": "career_goal",
                "memory_key": "target_role",
                "value": "AI Researcher",
            }
        ],
        "memory_updates": [
            {
                "action": "updated",
                "memory_type": "career_goal",
                "memory_key": "target_role",
            }
        ],
    }

    result = decide_module2_trigger(state)

    assert result["module2_triggered"] is True
    assert "career_goal_changed" in result["module2_trigger_reasons"]