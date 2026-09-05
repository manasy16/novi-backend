import uuid

from sqlalchemy.orm import Session

from app.db.models.student import Student


class StudentRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        student_id: uuid.UUID,
    ) -> Student | None:
        """
        Retrieve a student using the internal database UUID.
        """

        return db.get(Student, student_id)

    @staticmethod
    def get_by_external_id(
        db: Session,
        external_id: str,
    ) -> Student | None:
        """
        Retrieve a student using the external authentication ID.
        """

        return (
            db.query(Student)
            .filter(Student.external_id == external_id)
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        external_id: str,
    ) -> Student:
        """
        Create a new student.
        """

        student = Student(
            external_id=external_id
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        return student