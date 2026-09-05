import uuid
import time

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
    print("=" * 75)
    print(title)
    print("=" * 75)


def create_test_student(db):

    external_id = f"failed_case_test_{uuid.uuid4()}"

    student = StudentRepository.create(
        db=db,
        external_id=external_id,
    )

    print("\n✓ Test student created")
    print(f"External ID: {external_id}")
    print(f"Internal ID: {student.id}")

    return student, external_id


def invoke_graph(
    external_student_id: str,
    user_message: str,
    conversation_id=None,
):

    initial_state = {
        "external_student_id": external_student_id,
        "student_id": None,

        "conversation_id": conversation_id,
        "conversation_type": "onboarding",

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


# ============================================================
# TEST 1
# EMPTY MESSAGE
# ============================================================

def test_empty_message(external_id):

    print_separator(
        "TEST 1: EMPTY MESSAGE VALIDATION"
    )

    try:

        result = invoke_graph(
            external_student_id=external_id,
            user_message="",
        )

        print("\n✗ FAILED")
        print(
            "Empty message was accepted when it should "
            "have been rejected."
        )

        print(result)

        return False

    except ValueError as e:

        print("\n✓ PASSED")
        print("Empty message correctly rejected")
        print(f"Error: {str(e)}")

        return True

    except Exception as e:

        print("\n✗ FAILED WITH UNEXPECTED ERROR")
        print(type(e).__name__)
        print(str(e))

        return False


# ============================================================
# TEST 2
# WHITESPACE MESSAGE
# ============================================================

def test_whitespace_message(external_id):

    print_separator(
        "TEST 2: WHITESPACE MESSAGE VALIDATION"
    )

    try:

        result = invoke_graph(
            external_student_id=external_id,
            user_message="     ",
        )

        print("\n✗ FAILED")
        print(
            "Whitespace-only message was accepted."
        )

        print(result)

        return False

    except ValueError as e:

        print("\n✓ PASSED")
        print(
            "Whitespace message correctly rejected"
        )
        print(f"Error: {str(e)}")

        return True

    except Exception as e:

        print("\n✗ FAILED WITH UNEXPECTED ERROR")
        print(type(e).__name__)
        print(str(e))

        return False


# ============================================================
# TEST 3
# NON-EXISTENT STUDENT
# ============================================================

def test_nonexistent_student():

    print_separator(
        "TEST 3: NON-EXISTENT STUDENT"
    )

    fake_external_id = (
        f"does_not_exist_{uuid.uuid4()}"
    )

    try:

        result = invoke_graph(
            external_student_id=fake_external_id,
            user_message="I enjoy mathematics.",
        )

        print("\n✗ FAILED")
        print(
            "Graph accepted a student that does not exist."
        )

        print(result)

        return False

    except ValueError as e:

        print("\n✓ PASSED")
        print(
            "Non-existent student correctly rejected"
        )
        print(f"Error: {str(e)}")

        return True

    except Exception as e:

        print("\n✗ FAILED WITH UNEXPECTED ERROR")
        print(type(e).__name__)
        print(str(e))

        return False


# ============================================================
# TEST 4
# INVALID CONVERSATION ID
# ============================================================

def test_invalid_conversation(external_id):

    print_separator(
        "TEST 4: INVALID CONVERSATION ID"
    )

    fake_conversation_id = str(uuid.uuid4())

    try:

        result = invoke_graph(
            external_student_id=external_id,
            conversation_id=fake_conversation_id,
            user_message=(
                "I enjoy programming and mathematics."
            ),
        )

        print("\n✗ FAILED")
        print(
            "Graph accepted an invalid conversation ID."
        )

        print(result)

        return False

    except ValueError as e:

        print("\n✓ PASSED")
        print(
            "Invalid conversation correctly rejected"
        )
        print(f"Error: {str(e)}")

        return True

    except Exception as e:

        print("\n✗ FAILED WITH UNEXPECTED ERROR")
        print(type(e).__name__)
        print(str(e))

        return False


# ============================================================
# TEST 5
# LONG CONVERSATION
# ============================================================

def test_long_conversation(
    db,
    student,
    external_id,
):

    print_separator(
        "TEST 5: LONG CONVERSATION"
    )

    messages = [

        "I am currently studying computer science.",

        "I enjoy mathematics and logical reasoning.",

        "I have recently started learning Python.",

        "I find artificial intelligence very interesting.",

        "I want to understand machine learning properly.",

        "I enjoy solving difficult technical problems.",

        "I prefer analytical work over creative design.",

        "I think I would enjoy working with data.",

    ]

    conversation_id = None

    successful_messages = 0

    for index, message in enumerate(
        messages,
        start=1,
    ):

        print(f"\n--- MESSAGE {index} ---")
        print(f"User: {message}")

        try:

            result = invoke_graph(
                external_student_id=external_id,
                conversation_id=conversation_id,
                user_message=message,
            )

            conversation_id = result.get(
                "conversation_id"
            )

            assistant_response = result.get(
                "assistant_response"
            )

            provider = result.get(
                "llm_provider"
            )

            extracted_memories = result.get(
                "extracted_memories"
            ) or []

            print(
                f"Assistant: {assistant_response}"
            )

            print(
                f"Provider: {provider}"
            )

            print(
                f"Memories extracted: "
                f"{len(extracted_memories)}"
            )

            successful_messages += 1

        except Exception as e:

            print("\n✗ MESSAGE FAILED")
            print(
                f"Error Type: {type(e).__name__}"
            )
            print(
                f"Error: {str(e)}"
            )

            return False

        # Important: avoid rate limits
        if index < len(messages):

            print(
                "\nWaiting 2 seconds before next "
                "LLM request..."
            )

            time.sleep(2)

    # --------------------------------------------------------
    # DATABASE VERIFICATION
    # --------------------------------------------------------

    print("\n--- DATABASE VERIFICATION ---")

    if not conversation_id:

        print("✗ Conversation ID missing")
        return False

    conversation = (
        ConversationRepository.get_by_id(
            db=db,
            conversation_id=uuid.UUID(
                str(conversation_id)
            ),
        )
    )

    if not conversation:

        print("✗ Conversation not found")
        return False

    messages_db = (
        ConversationRepository.get_messages(
            db=db,
            conversation_id=conversation.id,
        )
    )

    memories = (
        MemoryRepository()
        .get_memories_by_student(
            db=db,
            student_id=student.id,
        )
    )

    print(
        f"✓ Successful graph calls: "
        f"{successful_messages}/{len(messages)}"
    )

    print(
        f"✓ Database messages: "
        f"{len(messages_db)}"
    )

    print(
        f"✓ Conversation message_count: "
        f"{conversation.message_count}"
    )

    print(
        f"✓ Memories stored: "
        f"{len(memories)}"
    )

    # Every user message should produce
    # one user + one assistant message
    expected_message_count = len(messages) * 2

    if len(messages_db) != expected_message_count:

        print(
            f"\n✗ FAILED: Expected "
            f"{expected_message_count} messages "
            f"but found {len(messages_db)}"
        )

        return False

    if conversation.message_count != expected_message_count:

        print(
            f"\n✗ FAILED: Conversation message_count "
            f"is incorrect."
        )

        return False

    print(
        "\n✓ PASSED: Long conversation completed "
        "successfully"
    )

    return True


# ============================================================
# TEST 6
# PROVIDER RELIABILITY
# ============================================================

def test_provider_reliability(external_id):

    print_separator(
        "TEST 6: LLM PROVIDER RELIABILITY"
    )

    provider_usage = []

    test_messages = [

        "I enjoy solving logical problems.",

        "I am interested in artificial intelligence.",

        "I want to learn machine learning.",

    ]

    conversation_id = None

    for index, message in enumerate(
        test_messages,
        start=1,
    ):

        print(f"\nRequest {index}")

        try:

            result = invoke_graph(
                external_student_id=external_id,
                conversation_id=conversation_id,
                user_message=message,
            )

            conversation_id = result.get(
                "conversation_id"
            )

            provider = result.get(
                "llm_provider"
            )

            provider_usage.append(provider)

            print(
                f"✓ Request succeeded using: {provider}"
            )

        except Exception as e:

            print(
                f"✗ Request {index} failed"
            )

            print(str(e))

            return False

        time.sleep(2)

    print("\nProvider usage:")

    for index, provider in enumerate(
        provider_usage,
        start=1,
    ):

        print(
            f"Request {index}: {provider}"
        )

    print(
        "\n✓ PASSED: Provider handled "
        "multiple sequential requests"
    )

    return True


# ============================================================
# MAIN
# ============================================================

def run_failed_case_tests():

    db = SessionLocal()

    results = {}

    try:

        print("\n")
        print("#" * 75)
        print("MODULE 1 - PREVIOUSLY FAILING CASES TEST")
        print("#" * 75)

        # ----------------------------------------------------
        # Create test student
        # ----------------------------------------------------

        student, external_id = create_test_student(db)

        # ----------------------------------------------------
        # TEST 1
        # ----------------------------------------------------

        results["Empty Message"] = (
            test_empty_message(external_id)
        )

        # ----------------------------------------------------
        # TEST 2
        # ----------------------------------------------------

        results["Whitespace Message"] = (
            test_whitespace_message(external_id)
        )

        # ----------------------------------------------------
        # TEST 3
        # ----------------------------------------------------

        results["Non-existent Student"] = (
            test_nonexistent_student()
        )

        # ----------------------------------------------------
        # TEST 4
        # ----------------------------------------------------

        results["Invalid Conversation"] = (
            test_invalid_conversation(external_id)
        )

        # ----------------------------------------------------
        # TEST 5
        # ----------------------------------------------------

        results["Long Conversation"] = (
            test_long_conversation(
                db=db,
                student=student,
                external_id=external_id,
            )
        )

        # ----------------------------------------------------
        # TEST 6
        # ----------------------------------------------------

        results["Provider Reliability"] = (
            test_provider_reliability(
                external_id
            )
        )

        # ----------------------------------------------------
        # FINAL REPORT
        # ----------------------------------------------------

        print_separator(
            "FINAL TEST REPORT"
        )

        passed = 0
        failed = 0

        for test_name, status in results.items():

            symbol = "✓ PASSED" if status else "✗ FAILED"

            print(
                f"{symbol} - {test_name}"
            )

            if status:
                passed += 1
            else:
                failed += 1

        print("\n" + "-" * 75)

        print(
            f"TOTAL: {len(results)}"
        )

        print(
            f"PASSED: {passed}"
        )

        print(
            f"FAILED: {failed}"
        )

        print("-" * 75)

        if failed == 0:

            print(
                "\n🎉 ALL PREVIOUSLY FAILING CASES "
                "PASSED SUCCESSFULLY"
            )

        else:

            print(
                "\n⚠ SOME CASES STILL REQUIRE FIXING"
            )

    finally:

        db.close()


if __name__ == "__main__":
    run_failed_case_tests()