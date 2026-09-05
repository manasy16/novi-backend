from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.memory import StudentMemory,MemoryVersion



class MemoryRepository:

    def create_memory(
        self,
        db: Session,
        student_id: UUID,
        memory_type: str,
        memory_key: str,
        value: str,
        normalized_value: str | None = None,
        confidence: float = 1.0,
        importance: int = 5,
        source: str = "conversation",
        metadata_json: dict | None = None,
    ) -> StudentMemory:

        memory = StudentMemory(
            student_id=student_id,
            memory_type=memory_type,
            memory_key=memory_key,
            value=value,
            normalized_value=normalized_value,
            confidence=confidence,
            importance=importance,
            source=source,
            is_active=True,
            version=1,
            metadata_json=metadata_json or {},
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        return memory

    def get_memories_by_student(
        self,
        db: Session,
        student_id: UUID,
        active_only: bool = True,
    ) -> list[StudentMemory]:

        query = db.query(StudentMemory).filter(
            StudentMemory.student_id == student_id
        )

        if active_only:
            query = query.filter(
                StudentMemory.is_active == True
            )

        return query.order_by(
            StudentMemory.importance.desc(),
            StudentMemory.updated_at.desc(),
        ).all()

    def get_memories_by_type(
        self,
        db: Session,
        student_id: UUID,
        memory_type: str,
    ) -> list[StudentMemory]:

        return (
            db.query(StudentMemory)
            .filter(
                StudentMemory.student_id == student_id,
                StudentMemory.memory_type == memory_type,
                StudentMemory.is_active == True,
            )
            .order_by(StudentMemory.updated_at.desc())
            .all()
        )

    def get_memory(
        self,
        db: Session,
        student_id: UUID,
        memory_type: str,
        memory_key: str,
    ) -> StudentMemory | None:

        return (
            db.query(StudentMemory)
            .filter(
                StudentMemory.student_id == student_id,
                StudentMemory.memory_type == memory_type,
                StudentMemory.memory_key == memory_key,
                StudentMemory.is_active == True,
            )
            .first()
        )

    def update_memory(
        self,
        db: Session,
        memory: StudentMemory,
        value: str,
        normalized_value: str | None = None,
        confidence: float = 1.0,
        change_reason: str | None = None,
        source_message_id: UUID | None = None,
    ) -> StudentMemory:

        # Store previous version in history
        version_entry = MemoryVersion(
            memory_id=memory.id,
            version=memory.version,
            value=memory.value,
            normalized_value=memory.normalized_value,
            confidence=memory.confidence,
            change_reason=change_reason,
            source_message_id=source_message_id,
            metadata_json=memory.metadata_json or {},
        )

        db.add(version_entry)

        # Update current memory
        memory.value = value
        memory.normalized_value = normalized_value
        memory.confidence = confidence
        memory.version += 1

        db.commit()
        db.refresh(memory)

        return memory

    def deactivate_memory(
        self,
        db: Session,
        memory: StudentMemory,
    ) -> StudentMemory:

        memory.is_active = False

        db.commit()
        db.refresh(memory)

        return memory