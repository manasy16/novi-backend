from app.auth.service import auth_service
from app.db.database import SessionLocal


db = SessionLocal()

try:
    email = "test@novi.com"
    password = "test123"

    user = auth_service.register(
        db=db,
        email=email,
        password=password,
    )

    print("USER CREATED:", user.id)
    print("STUDENT ID:", user.student_id)

    token = auth_service.authenticate(
        db=db,
        email=email,
        password=password,
    )

    print("TOKEN CREATED:", token[:30] + "...")

finally:
    db.close()