import uuid

from app.db.database import SessionLocal
from app.repositories.student_repository import StudentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.memory_repository import MemoryRepository
from app.graph.workflow import module1_graph


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_separator(title: str):
    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


def create_test_student(db):
    """
    Create a fresh student for testing.
    """

    external_id = f"edge_test_{uuid.uuid4()}"

    student = StudentRepository.create(
        db=db,
        external_id=external_id,
    )

    print(f"Student created")
    print(f"External ID: {external_id}")
    print(f"Internal ID: {student.id}")

    return student, external_id


def invoke_graph(
    external_student_id: str,
    user_message: str,
    conversation_id=None,
    conversation_type="onboarding",
):
    """
    Invoke Module 1 graph with a clean initial state.
    """

    initial_state = {
        "external_student_id": external_student_id,
        "student_id": None,

        "conversation_id": conversation_id,
        "conversation_type": conversation_type,

        "user_message": user_message,

        "student_profile": None,
        "recent_messages": [],
        "relevant_memories": [],

        "assistant_response": None,

        "extracted_memories": [],
        "memory_updates": [],

        "onboarding_status": "in_progress",

        "module2_triggered": False,

        "llm_provider": None,
    }

    return module1_graph.invoke(initial_state)


def print_result(result):
    """
    Print graph output in readable format.
    """

    print("\n--- GRAPH OUTPUT ---")

    print("\nConversation ID:")
    print(result.get("conversation_id"))

    print("\nAssistant Response:")
    print(result.get("assistant_response"))

    print("\nLLM Provider:")
    print(result.get("llm_provider"))

    print("\nExtracted Memories:")

    extracted_memories = result.get("extracted_memories") or []

    if not extracted_memories:
        print("None")
    else:
        for memory in extracted_memories:
            print(memory)

    print("\nMemory Updates:")

    memory_updates = result.get("memory_updates") or []

    if not memory_updates:
        print("None")
    else:
        for update in memory_updates:
            print(update)


def verify_conversation(db, conversation_id):
    """
    Verify conversation and messages exist in database.
    """

    print("\n--- DATABASE: CONVERSATION CHECK ---")

    if not conversation_id:
        print("✗ Conversation ID missing")
        return

    conversation = ConversationRepository.get_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        print("✗ Conversation not found")
        return

    print("✓ Conversation exists")
    print(f"Status: {conversation.status}")
    print(f"Message count: {conversation.message_count}")

    messages = ConversationRepository.get_messages(
        db=db,
        conversation_id=conversation_id,
    )

    print(f"\nMessages stored: {len(messages)}")

    for message in messages:
        print(
            f"[{message.sequence_number}] "
            f"{message.role}: "
            f"{message.content[:100]}"
        )


def verify_memories(db, student_id):
    """
    Print all active memories for a student.
    """

    print("\n--- DATABASE: MEMORY CHECK ---")

    memories = MemoryRepository().get_memories_by_student(
        db=db,
        student_id=student_id,
    )

    print(f"Total active memories: {len(memories)}")

    for memory in memories:

        print("\nMemory:")
        print(f"  ID: {memory.id}")
        print(f"  Type: {memory.memory_type}")
        print(f"  Key: {memory.memory_key}")
        print(f"  Value: {memory.value}")
        print(f"  Confidence: {memory.confidence}")
        print(f"  Importance: {memory.importance}")
        print(f"  Version: {memory.version}")


# ============================================================
# TEST CASE 1
# NEW STUDENT + FIRST MESSAGE
# ============================================================

def test_new_student_first_message(db):

    print_separator(
        "TEST CASE 1: NEW STUDENT FIRST MESSAGE"
    )

    student, external_id = create_test_student(db)

    result = invoke_graph(
        external_student_id=external_id,
        user_message=(
            "I really enjoy mathematics and logical problem solving. "
            "Recently I have become interested in artificial intelligence "
            "and machine learning. I want to build my career in AI."
        ),
    )

    print_result(result)

    verify_conversation(
        db,
        result.get("conversation_id"),
    )

    verify_memories(
        db,
        student.id,
    )

    return student, external_id, result


# ============================================================
# TEST CASE 2
# SAME CONVERSATION SECOND MESSAGE
# ============================================================

def test_existing_conversation(
    db,
    student,
    external_id,
    conversation_id,
):

    print_separator(
        "TEST CASE 2: EXISTING CONVERSATION"
    )

    result = invoke_graph(
        external_student_id=external_id,
        conversation_id=conversation_id,
        user_message=(
            "Apart from AI, I also enjoy programming in Python. "
            "I have started learning data structures and algorithms."
        ),
    )

    print_result(result)

    verify_conversation(
        db,
        result.get("conversation_id"),
    )

    verify_memories(
        db,
        student.id,
    )

    return result


# ============================================================
# TEST CASE 3
# MEMORY UPDATE
# ============================================================

def test_memory_update(
    db,
    student,
    external_id,
    conversation_id,
):

    print_separator(
        "TEST CASE 3: MEMORY UPDATE / VERSIONING"
    )

    result = invoke_graph(
        external_student_id=external_id,
        conversation_id=conversation_id,
        user_message=(
            "Actually I want to clarify something. "
            "I am not just casually interested in AI anymore. "
            "I am strongly committed to becoming a machine learning engineer."
        ),
    )

    print_result(result)

    verify_memories(
        db,
        student.id,
    )

    return result


# ============================================================
# TEST CASE 4
# NO IMPORTANT MEMORY
# ============================================================

def test_no_memory_message(
    db,
    student,
    external_id,
    conversation_id,
):

    print_separator(
        "TEST CASE 4: CASUAL MESSAGE WITH NO MEMORY"
    )

    result = invoke_graph(
        external_student_id=external_id,
        conversation_id=conversation_id,
        user_message=(
            "Okay, that sounds interesting. "
            "Can you tell me the next question?"
        ),
    )

    print_result(result)

    print("\nExpected:")
    print(
        "This message should ideally create "
        "zero important long-term memories."
    )

    verify_memories(
        db,
        student.id,
    )

    return result


# ============================================================
# TEST CASE 5
# MULTIPLE MEMORIES IN ONE MESSAGE
# ============================================================

def test_multiple_memories(
    db,
    student,
    external_id,
    conversation_id,
):

    print_separator(
        "TEST CASE 5: MULTIPLE MEMORIES"
    )

    result = invoke_graph(
        external_student_id=external_id,
        conversation_id=conversation_id,
        user_message=(
            "I enjoy solving difficult problems and working with data. "
            "I prefer analytical work rather than creative design. "
            "I also like working independently, although I can collaborate "
            "with a team when required. My strongest subjects are mathematics "
            "and computer science."
        ),
    )

    print_result(result)

    verify_memories(
        db,
        student.id,
    )

    return result


# ============================================================
# TEST CASE 6
# EMPTY MESSAGE
# ============================================================

def test_empty_message(
    external_id,
):

    print_separator(
        "TEST CASE 6: EMPTY MESSAGE"
    )

    try:

        result = invoke_graph(
            external_student_id=external_id,
            user_message="",
        )

        print_result(result)

        print("\n⚠ Empty message was accepted")

    except Exception as e:

        print("✓ Error handled correctly")
        print(f"Error: {str(e)}")


# ============================================================
# TEST CASE 7
# NON EXISTENT STUDENT
# ============================================================

def test_nonexistent_student():

    print_separator(
        "TEST CASE 7: NON-EXISTENT STUDENT"
    )

    fake_external_id = (
        f"nonexistent_{uuid.uuid4()}"
    )

    try:

        invoke_graph(
            external_student_id=fake_external_id,
            user_message="I like mathematics",
        )

        print("✗ ERROR: Graph should not succeed")

    except Exception as e:

        print("✓ Non-existent student handled")
        print(f"Error: {str(e)}")


# ============================================================
# TEST CASE 8
# MANY MESSAGES SEQUENCE
# ============================================================

def test_long_conversation(
    db,
    student,
    external_id,
):

    print_separator(
        "TEST CASE 8: LONG CONVERSATION FLOW"
    )

    conversation_id = None

    messages = [

        "I am currently studying computer science.",

        "I enjoy mathematics more than theoretical subjects.",

        "I like solving logical and analytical problems.",

        "I recently started learning Python.",

        "Machine learning looks very interesting to me.",

    ]

    for index, message in enumerate(messages, start=1):

        print(f"\n--- MESSAGE {index} ---")
        print(f"User: {message}")

        result = invoke_graph(
            external_student_id=external_id,
            conversation_id=conversation_id,
            user_message=message,
        )

        conversation_id = result.get("conversation_id")

        print(
            "Assistant:",
            result.get("assistant_response"),
        )

        print(
            "Memories extracted:",
            len(
                result.get("extracted_memories")
                or []
            ),
        )

    verify_conversation(
        db,
        conversation_id,
    )

    verify_memories(
        db,
        student.id,
    )


# ============================================================
# TEST CASE 9
# INVALID CONVERSATION ID
# ============================================================

def test_invalid_conversation(
    external_id,
):

    print_separator(
        "TEST CASE 9: INVALID CONVERSATION ID"
    )

    fake_conversation_id = str(uuid.uuid4())

    try:

        result = invoke_graph(
            external_student_id=external_id,
            conversation_id=fake_conversation_id,
            user_message="I like programming.",
        )

        print_result(result)

        print(
            "\n⚠ Check whether system correctly "
            "handles invalid conversation IDs."
        )

    except Exception as e:

        print("✓ Invalid conversation handled")
        print(f"Error: {str(e)}")


# ============================================================
# MAIN TEST RUNNER
# ============================================================

def run_all_tests():

    db = SessionLocal()

    try:

        print("\n")
        print("#" * 70)
        print("MODULE 1 COMPLETE GRAPH EDGE CASE TESTING")
        print("#" * 70)

        # ----------------------------------------------------
        # Create one student for main tests
        # ----------------------------------------------------

        student, external_id = create_test_student(db)

        # ----------------------------------------------------
        # TEST 1
        # ----------------------------------------------------

        print_separator(
            "TEST 1: FIRST MESSAGE"
        )

        result1 = invoke_graph(
            external_student_id=external_id,
            user_message=(
                "I really enjoy mathematics and logical problem solving. "
                "I am interested in AI and machine learning and want "
                "to build my career in this field."
            ),
        )

        print_result(result1)

        conversation_id = result1.get(
            "conversation_id"
        )

        verify_conversation(
            db,
            conversation_id,
        )

        verify_memories(
            db,
            student.id,
        )

        # ----------------------------------------------------
        # TEST 2
        # ----------------------------------------------------

        test_existing_conversation(
            db,
            student,
            external_id,
            conversation_id,
        )

        # ----------------------------------------------------
        # TEST 3
        # ----------------------------------------------------

        test_memory_update(
            db,
            student,
            external_id,
            conversation_id,
        )

        # ----------------------------------------------------
        # TEST 4
        # ----------------------------------------------------

        test_no_memory_message(
            db,
            student,
            external_id,
            conversation_id,
        )

        # ----------------------------------------------------
        # TEST 5
        # ----------------------------------------------------

        test_multiple_memories(
            db,
            student,
            external_id,
            conversation_id,
        )

        # ----------------------------------------------------
        # TEST 6
        # ----------------------------------------------------

        test_empty_message(
            external_id,
        )

        # ----------------------------------------------------
        # TEST 7
        # ----------------------------------------------------

        test_nonexistent_student()

        # ----------------------------------------------------
        # TEST 8
        # Fresh student for long conversation
        # ----------------------------------------------------

        long_student, long_external_id = (
            create_test_student(db)
        )

        test_long_conversation(
            db,
            long_student,
            long_external_id,
        )

        # ----------------------------------------------------
        # TEST 9
        # ----------------------------------------------------

        test_invalid_conversation(
            external_id,
        )

        print_separator(
            "ALL EDGE CASE TESTS COMPLETED"
        )

        print(
            "\nNow manually inspect the output for:"
        )

        print(
            "1. Conversation creation"
        )
        print(
            "2. Message persistence"
        )
        print(
            "3. Memory extraction accuracy"
        )
        print(
            "4. Duplicate memory prevention"
        )
        print(
            "5. Memory version updates"
        )
        print(
            "6. Context continuity"
        )
        print(
            "7. Invalid input handling"
        )

    finally:

        db.close()


if __name__ == "__main__":
    run_all_tests()