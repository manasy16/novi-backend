from app.db.database import SessionLocal
from app.repositories.conversation_repository import ConversationRepository
from app.graph.state.state import State1


def weekly_start_node(state: State1):
    db = SessionLocal()

    try:
        student_id = state["student_id"]

        conversation = ConversationRepository.create_conversation(
            db=db,
            student_id=student_id,
            conversation_type="weekly_update",
        )

        assistant_response = (
            "Hey! Let's do a quick weekly check-in. "
            "What have you been working on or learning this week?"
        )

        ConversationRepository.add_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_response,
        )

        return {
            "conversation_id": str(conversation.id),
            "assistant_response": assistant_response,
        }

    finally:
        db.close()