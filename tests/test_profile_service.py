from app.module2.services.profile_service import profile_service


def test_profile_builder():

    memories = [
        {
            "memory_type": "skill",
            "memory_key": "python",
            "value": "Python",
            "normalized_value": "python",
            "confidence": 0.9,
            "importance": 5,
        },
        {
            "memory_type": "interest",
            "memory_key": "ai_ml",
            "value": "AI/ML",
            "normalized_value": "ai/ml",
            "confidence": 0.8,
            "importance": 4,
        },
        {
            "memory_type": "career_goal",
            "memory_key": "target_role",
            "value": "AI/ML Engineer",
            "normalized_value": "ai/ml engineer",
            "confidence": 0.9,
            "importance": 5,
        },
    ]

    profile = profile_service.build_profile(memories)

    assert len(profile["skills"]) == 1
    assert profile["skills"][0]["key"] == "python"

    assert len(profile["interests"]) == 1
    assert profile["interests"][0]["key"] == "ai_ml"

    assert len(profile["career_goals"]) == 1
    assert profile["career_goals"][0]["key"] == "target_role"

    assert profile["total_facts"] == 3

    assert "skills" in profile["categories_present"]
    assert "interests" in profile["categories_present"]
    assert "career_goals" in profile["categories_present"]


def test_profile_builder_deduplicates():

    memories = [
        {
            "memory_type": "skill",
            "memory_key": "python",
            "value": "Python",
            "normalized_value": "python",
            "confidence": 0.9,
            "importance": 5,
        },
        {
            "memory_type": "skill",
            "memory_key": "python",
            "value": "Python",
            "normalized_value": "python",
            "confidence": 0.9,
            "importance": 5,
        },
    ]

    profile = profile_service.build_profile(memories)

    assert len(profile["skills"]) == 1
    assert profile["total_facts"] == 1

def test_profile_builder_ignores_unknown_memories():

    memories = [
        {
            "memory_type": "skill",
            "memory_key": "python",
            "value": "Python",
            "normalized_value": "python",
            "confidence": 0.9,
            "importance": 5,
        },
        {
            "memory_type": "random_unknown_type",
            "memory_key": "something",
            "value": "Something",
        },
        {
            "memory_key": "missing_type",
            "value": "Something",
        },
    ]

    profile = profile_service.build_profile(memories)

    assert len(profile["skills"]) == 1
    assert profile["total_facts"] == 1