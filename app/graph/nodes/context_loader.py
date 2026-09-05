from uuid import UUID

from app.db.database import SessionLocal
from app.repositories.student_repository import StudentRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.conversation_repository import ConversationRepository
from app.graph.state.state import State1


def load_context(state: State1):
    """
    Load student context and prepare the conversation.

    Responsibilities:
    1. Validate incoming message.
    2. Find the student using external_student_id from Auth.
    3. Create or retrieve conversation.
    4. Store current user message.
    5. Load student memories.
    6. Load recent conversation history.
    """

    # -------------------------------------------------
    # 1. VALIDATE USER MESSAGE BEFORE DB / LLM WORK
    # -------------------------------------------------

    user_message = state.get("user_message")

    if not user_message or not user_message.strip():
        raise ValueError(
            "User message cannot be empty"
        )

    db = SessionLocal()

    try:

        external_student_id = state["external_student_id"]

        # -------------------------------------------------
        # 2. FIND STUDENT
        # -------------------------------------------------

        student = StudentRepository.get_by_external_id(
            db,
            external_student_id,
        )

        if not student:
            raise ValueError(
                f"Student not found for external ID: "
                f"{external_student_id}"
            )

        # -------------------------------------------------
        # 3. GET OR CREATE CONVERSATION
        # -------------------------------------------------

        conversation_id = state.get("conversation_id")

        if conversation_id:

            if isinstance(conversation_id, str):
                conversation_id = UUID(conversation_id)

            conversation = ConversationRepository.get_by_id(
                db=db,
                conversation_id=conversation_id,
            )

            if not conversation:
                raise ValueError(
                    f"Conversation not found: {conversation_id}"
                )

        else:

            conversation_type = (
                state.get("conversation_type")
                or "onboarding"
            )

            conversation = (
                ConversationRepository.create_conversation(
                    db=db,
                    student_id=student.id,
                    conversation_type=conversation_type,
                )
            )

            conversation_id = conversation.id

        # -------------------------------------------------
        # 4. STORE USER MESSAGE
        # -------------------------------------------------

        ConversationRepository.add_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=user_message.strip(),
        )
        # -------------------------------------------------
        # 5. LOAD MEMORIES
        # -------------------------------------------------

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
        # -------------------------------------------------
        # 6. LOAD RECENT MESSAGES
        # -------------------------------------------------

        messages = ConversationRepository.get_messages(
            db=db,
            conversation_id=conversation_id,
        )

        recent_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages[-10:]
        ]
        # -------------------------------------------------
        # RETURN GRAPH STATE UPDATE
        # -------------------------------------------------

        result = {
            "student_id": student.id,
            "conversation_id": str(conversation_id),
            "student_profile": {
                "id": str(student.id),
                "external_id": student.external_id,
            },
            "relevant_memories": relevant_memories,
            "recent_messages": recent_messages,
        }

        return result

    finally:
        db.close()