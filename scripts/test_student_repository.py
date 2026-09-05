import uuid

from app.db.database import SessionLocal
from app.db.repositories.student_repository import StudentRepository


def test_student_repository():
    db = SessionLocal()

    try:
        external_id = f"test_student_{uuid.uuid4()}"

        # Create student
        student = StudentRepository.create(
            db=db,
            external_id=external_id,
        )

        print("\nStudent created successfully:")
        print(f"ID: {student.id}")
        print(f"External ID: {student.external_id}")

        # Fetch same student
        fetched_student = StudentRepository.get_by_id(
            db=db,
            student_id=student.id,
        )

        print("\nStudent fetched successfully:")
        print(f"ID: {fetched_student.id}")
        print(f"External ID: {fetched_student.external_id}")

    finally:
        db.close()


if __name__ == "__main__":
    test_student_repository()