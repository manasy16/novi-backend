from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.module2.repositories.intelligence_repository import (
    IntelligenceRepository,
)
from app.module2.schemas.output import StudentIntelligenceResponse


router = APIRouter(
    prefix="/module2",
    tags=["Module 2"],
)


@router.get(
    "/intelligence",
    response_model=StudentIntelligenceResponse,
)
def get_latest_intelligence(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    intelligence = IntelligenceRepository.get_latest_intelligence(
        db=db,
        student_id=current_user.student_id,
    )

    if intelligence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student intelligence not found",
        )

    return intelligence