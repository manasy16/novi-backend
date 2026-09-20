from app.graph.state.state import State1


SIGNIFICANT_MEMORY_TYPES = {
    "career_goal",
    "project",
    "achievement",
    "experience",
}


def decide_module2_trigger(state: State1):

    extracted_memories = state.get("extracted_memories", [])
    memory_updates = state.get("memory_updates", [])

    reasons = []

    # --------------------------------------------------
    # 1. Explicitly changed existing information
    # --------------------------------------------------

    for update in memory_updates:

        if update.get("action") == "updated":

            memory_type = update.get("memory_type")

            if memory_type == "career_goal":
                reasons.append("career_goal_changed")

            elif memory_type in SIGNIFICANT_MEMORY_TYPES:
                reasons.append(f"{memory_type}_changed")

    # --------------------------------------------------
    # 2. New significant information
    # --------------------------------------------------

    for memory in extracted_memories:

        memory_type = memory.get("memory_type")

        if memory_type in SIGNIFICANT_MEMORY_TYPES:

            # Only treat it as new if the updater actually
            # created it.
            memory_key = memory.get("memory_key")

            created = any(
                update.get("action") == "created"
                and update.get("memory_type") == memory_type
                and update.get("memory_key") == memory_key
                for update in memory_updates
            )

            if created:
                reasons.append(f"new_{memory_type}")

    # --------------------------------------------------
    # 3. Remove duplicate reasons
    # --------------------------------------------------

    reasons = list(dict.fromkeys(reasons))

    return {
        "module2_triggered": bool(reasons),
        "module2_trigger_reasons": reasons,
    }