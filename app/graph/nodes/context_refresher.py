from uuid import UUID

from app.db.database import SessionLocal
from app.repositories.memory_repository import MemoryRepository
from app.graph.state.state import State1


def refresh_context(state: State1) -> dict:
    """
    Refresh student memories after memory updates.

    This node must NOT:
    - create a conversation
    - store any messages

    It only reloads the latest memories from the database.
    """

    student_id = state.get("student_id")

    if not student_id:
        raise ValueError(
            "student_id is required to refresh context"
        )

    db = SessionLocal()

    try:

        memories = (
            MemoryRepository()
            .get_memories_by_student(
                db=db,
                student_id=UUID(str(student_id)),
            )
        )

        relevant_memories = [
            {
                "id": str(memory.id),
                "memory_type": memory.memory_type,
                "memory_key": memory.memory_key,
                "value": memory.value,
                "normalized_value": memory.normalized_value,
                "confidence": memory.confidence,
                "importance": memory.importance,
            }
            for memory in memories
        ]

        result = {
            "relevant_memories": relevant_memories,
        }
        return result

    finally:
        db.close()