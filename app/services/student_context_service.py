from uuid import UUID

from app.db.database import SessionLocal
from app.repositories.student_repository import StudentRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.conversation_repository import ConversationRepository


class StudentContextService:

    @staticmethod
    def get_context(
        external_student_id: str,
        conversation_id: str | UUID | None = None,
    ) -> dict:

        db = SessionLocal()

        try:
            # -----------------------------------------
            # 1. FIND STUDENT
            # -----------------------------------------

            student = StudentRepository.get_by_external_id(
                db,
                external_student_id,
            )

            if not student:
                raise ValueError(
                    f"Student not found for external ID: "
                    f"{external_student_id}"
                )

            # -----------------------------------------
            # 2. GET EXISTING CONVERSATION
            # -----------------------------------------

            resolved_conversation_id = None

            if conversation_id:

                if isinstance(conversation_id, str):
                    conversation_id = UUID(conversation_id)

                conversation = (
                    ConversationRepository.get_by_id(
                        db=db,
                        conversation_id=conversation_id,
                    )
                )

                if not conversation:
                    raise ValueError(
                        f"Conversation not found: "
                        f"{conversation_id}"
                    )

                resolved_conversation_id = conversation.id

            # -----------------------------------------
            # 3. LOAD MEMORIES
            # -----------------------------------------

            memories = (
                MemoryRepository()
                .get_memories_by_student(
                    db=db,
                    student_id=student.id,
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

            # -----------------------------------------
            # 4. LOAD CONVERSATION HISTORY
            # -----------------------------------------

            recent_messages = []

            if resolved_conversation_id:

                messages = (
                    ConversationRepository.get_messages(
                        db=db,
                        conversation_id=resolved_conversation_id,
                    )
                )

                recent_messages = [
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in messages[-10:]
                ]

            # -----------------------------------------
            # 5. RETURN CONTEXT
            # -----------------------------------------

            return {
                "student": student,
                "student_id": student.id,
                "conversation_id": (
                    str(resolved_conversation_id)
                    if resolved_conversation_id
                    else None
                ),
                "student_profile": {
                    "id": str(student.id),
                    "external_id": student.external_id,
                },
                "relevant_memories": relevant_memories,
                "recent_messages": recent_messages,
            }

        finally:
            db.close()


student_context_service = StudentContextService()