from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.graph.workflow import module1_graph


router = APIRouter(
    prefix="/module1",
    tags=["Module 1"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    conversation_id: str | None = None
    assistant_response: str
    onboarding_status: str | None = None
    completion_percentage: int = 0
    missing_categories: list[str] = []


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    state = {
        "external_student_id": str(current_user.student.external_id),
        "student_id": current_user.student_id,
        "user_message": request.message,
        "conversation_type": "onboarding",
    }

    result = module1_graph.invoke(state)

    return ChatResponse(
        conversation_id=(
            str(result["conversation_id"])
            if result.get("conversation_id")
            else None
        ),
        assistant_response=result.get("assistant_response", ""),
        onboarding_status=result.get("onboarding_status"),
        completion_percentage=result.get("completion_percentage", 0),
        missing_categories=result.get("missing_categories", []),
    )