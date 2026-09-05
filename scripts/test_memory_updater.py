import uuid

from app.db.database import SessionLocal
from app.repositories.student_repository import StudentRepository
from app.repositories.memory_repository import MemoryRepository
from app.graph.nodes.memory_updater import memory_updater_node


def print_updates(title, result):
    print(f"\n--- {title} ---")

    updates = result.get("memory_updates", [])

    for update in updates:
        print(update)


def test_memory_updater():

    print("\n========== MEMORY UPDATER TEST ==========")

    db = SessionLocal()

    try:
        # -----------------------------------------
        # CREATE TEST STUDENT
        # -----------------------------------------

        external_id = f"memory_updater_test_{uuid.uuid4()}"

        student = StudentRepository.create(
            db=db,
            external_id=external_id,
        )

        print("\nTest Student Created")
        print("Student ID:", student.id)

        student_id = student.id

    finally:
        db.close()

    # =============================================
    # TEST 1: CREATE NEW MEMORY
    # =============================================

    state = {
        "student_id": student_id,
        "extracted_memories": [
            {
                "memory_type": "interest",
                "memory_key": "mathematics",
                "value": "Student enjoys mathematics",
                "normalized_value": "mathematics",
                "confidence": 0.9,
                "importance": 8,
            }
        ],
    }

    result = memory_updater_node(state)

    print_updates(
        "TEST 1: CREATE NEW MEMORY",
        result,
    )

    # =============================================
    # TEST 2: SAME MEMORY AGAIN
    # Should remain unchanged
    # =============================================

    result = memory_updater_node(state)

    print_updates(
        "TEST 2: DUPLICATE MEMORY",
        result,
    )

    # =============================================
    # TEST 3: UPDATE EXISTING MEMORY
    # Same type + key, different value
    # =============================================

    updated_state = {
        "student_id": student_id,
        "extracted_memories": [
            {
                "memory_type": "interest",
                "memory_key": "mathematics",
                "value": (
                    "Student strongly enjoys mathematics "
                    "and advanced problem solving"
                ),
                "normalized_value": "mathematics",
                "confidence": 0.95,
                "importance": 9,
            }
        ],
    }

    result = memory_updater_node(updated_state)

    print_updates(
        "TEST 3: UPDATE EXISTING MEMORY",
        result,
    )

    # =============================================
    # TEST 4: MULTIPLE NEW MEMORIES
    # =============================================

    multiple_memory_state = {
        "student_id": student_id,
        "extracted_memories": [
            {
                "memory_type": "skill",
                "memory_key": "python",
                "value": "Student knows Python",
                "normalized_value": "python",
                "confidence": 0.95,
                "importance": 8,
            },
            {
                "memory_type": "career_goal",
                "memory_key": "machine_learning_engineer",
                "value": (
                    "Student wants to become a "
                    "machine learning engineer"
                ),
                "normalized_value": (
                    "machine_learning_engineer"
                ),
                "confidence": 0.9,
                "importance": 10,
            },
            {
                "memory_type": "learning_style",
                "memory_key": "practical_learning",
                "value": (
                    "Student prefers learning through "
                    "projects and practical problems"
                ),
                "normalized_value": "practical_learning",
                "confidence": 0.9,
                "importance": 8,
            },
        ],
    }

    result = memory_updater_node(
        multiple_memory_state
    )

    print_updates(
        "TEST 4: MULTIPLE NEW MEMORIES",
        result,
    )

    # =============================================
    # TEST 5: EMPTY MEMORY LIST
    # =============================================

    empty_state = {
        "student_id": student_id,
        "extracted_memories": [],
    }

    result = memory_updater_node(empty_state)

    print_updates(
        "TEST 5: EMPTY MEMORY LIST",
        result,
    )

    # =============================================
    # FINAL DATABASE VERIFICATION
    # =============================================

    db = SessionLocal()

    try:

        memory_repository = MemoryRepository()

        memories = (
            memory_repository.get_memories_by_student(
                db=db,
                student_id=student_id,
            )
        )

        print("\n========== FINAL DATABASE CHECK ==========")

        print(
            f"\nTotal Active Memories: {len(memories)}"
        )

        for memory in memories:

            print("\nMemory")
            print("ID:", memory.id)
            print("Type:", memory.memory_type)
            print("Key:", memory.memory_key)
            print("Value:", memory.value)
            print("Version:", memory.version)
            print("Confidence:", memory.confidence)
            print("Importance:", memory.importance)

        # Expected:
        # mathematics
        # python
        # machine_learning_engineer
        # practical_learning

        print("\n========== TEST COMPLETED ==========")

    finally:
        db.close()


if __name__ == "__main__":
    test_memory_updater()