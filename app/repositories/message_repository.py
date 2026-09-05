from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.conversation import Message


class MessageRepository:

    def create_message(
        self,
        db: Session,
        conversation_id: UUID,
        role: str,
        content: str,
        sequence_number: int,
        metadata_json: dict | None = None,
    ) -> Message:

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            metadata_json=metadata_json or {},
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    def get_messages_by_conversation(
        self,
        db: Session,
        conversation_id: UUID,
    ) -> list[Message]:

        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number.asc())
            .all()
        )