import uuid

from app.db.database import SessionLocal
from app.repositories.student_repository import StudentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.memory_repository import MemoryRepository

from app.db.models.memory import MemoryVersion


def test_memory_flow():

    db = SessionLocal()

    student_repository = StudentRepository()
    conversation_repository = ConversationRepository()
    message_repository = MessageRepository()
    memory_repository = MemoryRepository()

    try:
        print("\n--- STEP 1: Creating Student ---")

        external_id = f"test_student_{uuid.uuid4()}"

        student = student_repository.create(
            db=db,
            external_id=external_id,
        )

        print(f"Student created: {student.id}")

        print("\n--- STEP 2: Creating Conversation ---")

        conversation = conversation_repository.create_conversation(
            db=db,
            student_id=student.id,
            conversation_type="onboarding",
        )

        print(f"Conversation created: {conversation.id}")

        print("\n--- STEP 3: Creating Messages ---")

        message_1 = message_repository.create_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content="What subjects do you enjoy the most?",
            sequence_number=1,
        )

        message_2 = message_repository.create_message(
            db=db,
            conversation_id=conversation.id,
            role="student",
            content="I really enjoy mathematics and solving logical problems.",
            sequence_number=2,
        )

        print("Messages stored successfully")

        print("\n--- STEP 4: Creating Memory ---")

        memory = memory_repository.create_memory(
            db=db,
            student_id=student.id,
            memory_type="interest",
            memory_key="mathematics",
            value="Student enjoys mathematics and logical problem solving",
            normalized_value="mathematics",
            confidence=0.95,
            importance=9,
            source="onboarding",
        )

        print(f"Memory created: {memory.value}")
        print(f"Version: {memory.version}")

        print("\n--- STEP 5: Updating Memory ---")

        updated_memory = memory_repository.update_memory(
            db=db,
            memory=memory,
            value="Student strongly enjoys mathematics, logical reasoning and problem solving",
            normalized_value="mathematics",
            confidence=0.98,
            change_reason="Student provided more detailed information",
            source_message_id=message_2.id,
        )

        print(f"Updated memory: {updated_memory.value}")
        print(f"Current version: {updated_memory.version}")

        print("\n--- STEP 6: Checking Memory History ---")

        versions = (
            db.query(MemoryVersion)
            .filter(MemoryVersion.memory_id == memory.id)
            .all()
        )

        for version in versions:
            print(
                f"History Version {version.version}: "
                f"{version.value}"
            )

        print("\n--- ALL TESTS COMPLETED SUCCESSFULLY ---")

    finally:
        db.close()


if __name__ == "__main__":
    test_memory_flow()