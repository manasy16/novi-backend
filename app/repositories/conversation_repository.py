import uuid

from sqlalchemy.orm import Session

from app.db.models.conversation import Conversation,Message



class ConversationRepository:

    @staticmethod
    def create_conversation(
        db: Session,
        student_id: uuid.UUID,
        conversation_type: str,
    ) -> Conversation:
        """
        Create a new conversation for a student.
        """

        conversation = Conversation(
            student_id=student_id,
            conversation_type=conversation_type,
            status="active",
            message_count=0,
            metadata_json={},
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_by_id(
        db: Session,
        conversation_id: uuid.UUID,
    ) -> Conversation | None:
        """
        Get a conversation by its ID.
        """

        return db.get(Conversation, conversation_id)

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
    ) -> Message:
        """
        Add a message to a conversation.
        """

        conversation = db.get(
            Conversation,
            conversation_id,
        )

        if not conversation:
            raise ValueError("Conversation not found")

        next_sequence = conversation.message_count + 1

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence_number=next_sequence,
            metadata_json={},
        )

        db.add(message)

        conversation.message_count = next_sequence

        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: uuid.UUID,
    ) -> list[Message]:
        """
        Get all messages from a conversation in order.
        """

        return (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .order_by(Message.sequence_number.asc())
            .all()
        )

    @staticmethod
    def close_conversation(
        db: Session,
        conversation_id: uuid.UUID,
    ) -> Conversation | None:
        """
        Mark a conversation as completed.
        """

        conversation = db.get(
            Conversation,
            conversation_id,
        )

        if not conversation:
            return None

        conversation.status = "completed"

        db.commit()
        db.refresh(conversation)

        return conversation