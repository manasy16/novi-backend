import uuid

from app.db.database import SessionLocal
from app.repositories.student_repository import StudentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.memory_repository import MemoryRepository
from app.graph.workflow import module1_graph


def print_turn_result(turn_number, result):
    print("\n" + "=" * 70)
    print(f"TURN {turn_number} RESULT")
    print("=" * 70)

    print("\nAssistant Response:")
    print(result.get("assistant_response"))

    print("\nLLM Provider:")
    print(result.get("llm_provider"))

    print("\nExtracted Memories:")

    extracted_memories = result.get(
        "extracted_memories",
        [],
    )

    if extracted_memories:
        for memory in extracted_memories:
            print(memory)
    else:
        print("None")

    print("\nMemory Updates:")

    memory_updates = result.get(
        "memory_updates",
        [],
    )

    if memory_updates:
        for update in memory_updates:
            print(update)
    else:
        print("None")

    print("\nOnboarding Status:")
    print(result.get("onboarding_status"))

    print("\nCompletion Percentage:")
    print(result.get("completion_percentage"))

    print("\nCompleted Categories:")
    print(result.get("completed_categories"))

    print("\nMissing Categories:")
    print(result.get("missing_categories"))


def test_full_onboarding_flow():

    print("\n")
    print("=" * 70)
    print("FULL MULTI-TURN ONBOARDING INTEGRATION TEST")
    print("=" * 70)

    # --------------------------------------------------
    # STEP 1: CREATE TEST STUDENT
    # --------------------------------------------------

    external_id = (
        f"full_onboarding_test_{uuid.uuid4()}"
    )

    db = SessionLocal()

    try:

        student = StudentRepository.create(
            db=db,
            external_id=external_id,
        )

        student_id = student.id

        print("\nTest Student Created")
        print("External ID:", external_id)
        print("Student ID:", student_id)

    finally:
        db.close()

    # --------------------------------------------------
    # TEST CONVERSATION
    # --------------------------------------------------

    conversation_id = None

    turns = [

        # TURN 1
        {
            "message": (
                "I am currently a second year B.Tech "
                "Computer Science student."
            ),
            "expected_min_progress": 20,
        },

        # TURN 2
        {
            "message": (
                "I really enjoy mathematics, logical "
                "problem solving and artificial intelligence."
            ),
            "expected_min_progress": 40,
        },

        # TURN 3
        {
            "message": (
                "I know Python and have worked on a few "
                "small machine learning projects."
            ),
            "expected_min_progress": 60,
        },

        # TURN 4
        {
            "message": (
                "My goal is to become a machine learning "
                "engineer and work on impactful AI products."
            ),
            "expected_min_progress": 80,
        },

        # TURN 5
        {
            "message": (
                "I learn best when I first understand the "
                "concept and then apply it by building "
                "projects and solving practical problems."
            ),
            "expected_min_progress": 100,
        },
    ]

    # --------------------------------------------------
    # RUN MULTIPLE TURNS
    # --------------------------------------------------

    for index, turn in enumerate(turns, start=1):

        print("\n")
        print("#" * 70)
        print(f"STARTING TURN {index}")
        print("#" * 70)

        initial_state = {

            "external_student_id": external_id,

            "conversation_id": conversation_id,

            "conversation_type": "onboarding",

            "user_message": turn["message"],

            "recent_messages": [],

            "relevant_memories": [],

            "module2_triggered": False,
        }

        result = module1_graph.invoke(
            initial_state
        )

        # Preserve conversation across turns
        conversation_id = result.get(
            "conversation_id"
        )

        print_turn_result(
            index,
            result,
        )

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        completion_percentage = result.get(
            "completion_percentage",
            0,
        )

        expected_progress = turn[
            "expected_min_progress"
        ]

        if completion_percentage >= expected_progress:

            print(
                f"\n✓ TURN {index} PROGRESS CHECK PASSED "
                f"({completion_percentage}%)"
            )

        else:

            print(
                f"\n✗ TURN {index} PROGRESS CHECK FAILED"
            )

            print(
                f"Expected at least: "
                f"{expected_progress}%"
            )

            print(
                f"Actual: "
                f"{completion_percentage}%"
            )

    # --------------------------------------------------
    # FINAL DATABASE VERIFICATION
    # --------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL DATABASE VERIFICATION")
    print("=" * 70)

    db = SessionLocal()

    try:

        # ----------------------------------------------
        # CONVERSATION CHECK
        # ----------------------------------------------

        if conversation_id:

            conversation = (
                ConversationRepository.get_by_id(
                    db=db,
                    conversation_id=conversation_id,
                )
            )

            if conversation:

                print(
                    "\n✓ Conversation exists"
                )

                print(
                    "Conversation ID:",
                    conversation.id,
                )

                print(
                    "Message Count:",
                    conversation.message_count,
                )

                messages = (
                    ConversationRepository.get_messages(
                        db=db,
                        conversation_id=conversation_id,
                    )
                )

                print(
                    f"\nTotal Messages Stored: "
                    f"{len(messages)}"
                )

                for message in messages:

                    preview = (
                        message.content[:100]
                    )

                    print(
                        f"[{message.sequence_number}] "
                        f"{message.role}: "
                        f"{preview}"
                    )

            else:

                print(
                    "\n✗ Conversation not found"
                )

        else:

            print(
                "\n✗ Conversation ID missing"
            )

        # ----------------------------------------------
        # MEMORY CHECK
        # ----------------------------------------------

        memory_repository = MemoryRepository()

        memories = (
            memory_repository.get_memories_by_student(
                db=db,
                student_id=student_id,
            )
        )

        print(
            f"\nTotal Active Memories: "
            f"{len(memories)}"
        )

        for memory in memories:

            print("\nMemory:")
            print(
                "Type:",
                memory.memory_type,
            )
            print(
                "Key:",
                memory.memory_key,
            )
            print(
                "Value:",
                memory.value,
            )
            print(
                "Version:",
                memory.version,
            )

        # ----------------------------------------------
        # EXPECTED FINAL CATEGORIES
        # ----------------------------------------------

        memory_types = {
            memory.memory_type
            for memory in memories
        }

        print("\nFinal Memory Categories:")
        print(sorted(memory_types))

        required_categories = {
            "education",
            "interest",
            "skill",
            "career_goal",
        }

        missing_required = (
            required_categories - memory_types
        )

        if not missing_required:

            print(
                "\n✓ Core onboarding categories stored"
            )

        else:

            print(
                "\n✗ Missing categories:"
            )
            print(missing_required)

        # learning_style OR learning_preference accepted

        if (
            "learning_style" in memory_types
            or "learning_preference"
            in memory_types
        ):

            print(
                "✓ Learning preference stored"
            )

        else:

            print(
                "✗ Learning preference missing"
            )

    finally:
        db.close()

    print("\n")
    print("=" * 70)
    print("FULL ONBOARDING TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    test_full_onboarding_flow()