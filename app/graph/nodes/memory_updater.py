from app.db.database import SessionLocal
from app.repositories.memory_repository import MemoryRepository
from app.graph.state.state import State1


def memory_updater_node(state: State1):

    db = SessionLocal()
    memory_repository = MemoryRepository()

    try:

        student_id = state["student_id"]
        extracted_memories = state.get(
            "extracted_memories",
            []
        )
        memory_updates = []

        for extracted_memory in extracted_memories:

            memory_type = extracted_memory["memory_type"]
            memory_key = extracted_memory["memory_key"]
            value = extracted_memory["value"]
            normalized_value = extracted_memory.get(
                "normalized_value"
            )

            confidence = extracted_memory.get(
                "confidence",
                0.8
            )

            importance = extracted_memory.get(
                "importance",
                5
            )

            # ----------------------------------------
            # Check existing memory
            # ----------------------------------------

            existing_memory = memory_repository.get_memory(
                db=db,
                student_id=student_id,
                memory_type=memory_type,
                memory_key=memory_key,
            )

            # ----------------------------------------
            # CREATE
            # ----------------------------------------

            if existing_memory is None:

                new_memory = memory_repository.create_memory(
                    db=db,
                    student_id=student_id,
                    memory_type=memory_type,
                    memory_key=memory_key,
                    value=value,
                    normalized_value=normalized_value,
                    confidence=confidence,
                    importance=importance,
                    source="conversation",
                )

                memory_updates.append(
                    {
                        "action": "created",
                        "memory_id": str(new_memory.id),
                        "memory_type": memory_type,
                        "memory_key": memory_key,
                        "value": value,
                    }
                )
            # ----------------------------------------
            # UPDATE
            # ----------------------------------------

            else:

                # Avoid unnecessary version creation
                if (
                    existing_memory.value != value
                    or existing_memory.normalized_value
                    != normalized_value
                ):

                    updated_memory = (
                        memory_repository.update_memory(
                            db=db,
                            memory=existing_memory,
                            value=value,
                            normalized_value=normalized_value,
                            confidence=confidence,
                            change_reason=(
                                "Updated from new conversation"
                            ),
                        )
                    )

                    memory_updates.append(
                        {
                            "action": "updated",
                            "memory_id": str(updated_memory.id),
                            "memory_type": memory_type,
                            "memory_key": memory_key,
                            "value": value,
                            "version": updated_memory.version,
                        }
                    )
                else:

                    memory_updates.append(
                        {
                            "action": "unchanged",
                            "memory_id": str(existing_memory.id),
                            "memory_type": memory_type,
                            "memory_key": memory_key,
                            "value": existing_memory.value,
                            "version": existing_memory.version,
                        }
                    )
        result = {
            "memory_updates": memory_updates
        }
        return result

    finally:
        db.close()