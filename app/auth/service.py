from sqlalchemy.orm import Session

from app.db.models.user import User
from app.repositories.student_repository import StudentRepository
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.core.config import settings


class AuthService:

    @staticmethod
    def register(
        db: Session,
        email: str,
        password: str,
    ) -> User:

        existing_user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            raise ValueError("Email already registered")

        # For now email acts as the external authentication ID.
        student = StudentRepository.get_by_external_id(
            db=db,
            external_id=email,
        )

        if student is None:
            student = StudentRepository.create(
                db=db,
                external_id=email,
            )

        user = User(
            student_id=student.id,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate(
        db: Session,
        email: str,
        password: str,
    ) -> str:

        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if user is None:
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "student_id": str(user.student_id),
                "email": user.email,
            },
            expires_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return access_token


auth_service = AuthService()