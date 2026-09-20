from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

from app.auth.dependencies import get_current_user, get_db
from app.db.models.user import User

from app.graph.workflow import module1_graph
from app.graph.weekly_workflow import weekly_graph

from app.services.student_context_service import (
    student_context_service
)

from app.graph.nodes.session_node import (
    session_opening_node
)

from app.graph.nodes.weekly_start import (
    weekly_start_node
)
from app.services.weekly_summary_service import (
    weekly_summary_service
)

router = APIRouter(
    prefix="/module1",
    tags=["Module 1"],
)


# =========================================================
# REQUEST / RESPONSE SCHEMAS
# =========================================================

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str | None = None
    assistant_response: str

    onboarding_status: str | None = None
    completion_percentage: int = 0
    missing_categories: list[str] = []


# =========================================================
# WEEKLY UPDATE SCHEMAS
# =========================================================

class WeeklyStartResponse(BaseModel):
    conversation_id: str
    assistant_response: str


class WeeklyChatRequest(BaseModel):
    message: str
    conversation_id: str


class WeeklyChatResponse(BaseModel):
    conversation_id: str
    assistant_response: str
    memory_updates: list[dict] = []


class WeeklyCompleteRequest(BaseModel):
    conversation_id: str


class WeeklyCompleteResponse(BaseModel):
    conversation_id: str
    weekly_update_summary: dict
    module2_triggered: bool = False


# =========================================================
# CHAT
# =========================================================

@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    state = {
        "external_student_id": str(
            current_user.student.external_id
        ),

        "student_id": current_user.student_id,

        "user_message": request.message,

        "conversation_type": "onboarding",
    }

    # -----------------------------------------------------
    # CONTINUE EXISTING CONVERSATION
    # -----------------------------------------------------

    if request.conversation_id:

        state["conversation_id"] = (
            request.conversation_id
        )

    # -----------------------------------------------------
    # RUN MODULE 1
    # -----------------------------------------------------

    result = module1_graph.invoke(
        state,
        context={
            "db": db,
        },
    )

    # -----------------------------------------------------
    # RETURN RESPONSE
    # -----------------------------------------------------

    return ChatResponse(

        conversation_id=(
            str(result["conversation_id"])
            if result.get("conversation_id")
            else None
        ),

        assistant_response=result.get(
            "assistant_response",
            ""
        ),

        onboarding_status=result.get(
            "onboarding_status"
        ),

        completion_percentage=result.get(
            "completion_percentage",
            0
        ),

        missing_categories=result.get(
            "missing_categories",
            []
        ),
    )


# =========================================================
# SESSION / APP OPEN
# =========================================================

@router.get("/session")
def get_session(
    current_user: User = Depends(get_current_user),
):

    # -----------------------------------------------------
    # LOAD EXISTING STUDENT CONTEXT
    # -----------------------------------------------------

    context = (
        student_context_service.get_context(
            external_student_id=str(
                current_user.student.external_id
            )
        )
    )

    # -----------------------------------------------------
    # BUILD SESSION STATE
    # -----------------------------------------------------

    state = {

        "student_id":
            context["student_id"],

        "external_student_id":
            str(
                current_user.student.external_id
            ),

        "conversation_id":
            context["conversation_id"],

        "student_profile":
            context["student_profile"],

        "relevant_memories":
            context["relevant_memories"],

        "recent_messages":
            context["recent_messages"],
    }

    # -----------------------------------------------------
    # GENERATE PERSONALIZED OPENING
    # -----------------------------------------------------

    result = session_opening_node(
        state
    )

    # -----------------------------------------------------
    # RETURN SESSION INFORMATION
    # -----------------------------------------------------

    return {

        "conversation_id":
            context["conversation_id"],

        "assistant_response":
            result["assistant_response"],

        "onboarding_status":
            result["onboarding_status"],

        "completion_percentage":
            result["completion_percentage"],

        "missing_categories":
            result["missing_categories"],
    }


# =========================================================
# WEEKLY UPDATE - START
# =========================================================

@router.post(
    "/weekly/start",
    response_model=WeeklyStartResponse
)
def start_weekly_update(
    current_user: User = Depends(get_current_user),
):

    # -----------------------------------------------------
    # BUILD WEEKLY UPDATE STATE
    # -----------------------------------------------------

    state = {

        "student_id":
            current_user.student_id,

        "external_student_id":
            str(
                current_user.student.external_id
            ),
    }

    # -----------------------------------------------------
    # CREATE WEEKLY CONVERSATION
    # -----------------------------------------------------

    result = weekly_start_node(
        state
    )

    # -----------------------------------------------------
    # RETURN RESPONSE
    # -----------------------------------------------------

    return WeeklyStartResponse(

        conversation_id=
            result["conversation_id"],

        assistant_response=
            result["assistant_response"],
    )

# =========================================================
# WEEKLY UPDATE - CHAT
# =========================================================

@router.post(
    "/weekly/chat",
    response_model=WeeklyChatResponse
)
def weekly_chat(
    request: WeeklyChatRequest,
    current_user: User = Depends(get_current_user),
):
    # -----------------------------------------------------
    # BUILD WEEKLY CHAT STATE
    # -----------------------------------------------------

    state = {
        "student_id": current_user.student_id,

        "external_student_id": str(
            current_user.student.external_id
        ),

        "user_message": request.message,

        "conversation_id": request.conversation_id,

        "conversation_type": "weekly_update",
    }

    # -----------------------------------------------------
    # RUN WEEKLY GRAPH
    # -----------------------------------------------------

    result = weekly_graph.invoke(state)

    # -----------------------------------------------------
    # RETURN RESPONSE
    # -----------------------------------------------------

    return WeeklyChatResponse(
        conversation_id=str(
            result["conversation_id"]
        ),

        assistant_response=result.get(
            "assistant_response",
            ""
        ),

        memory_updates=result.get(
            "memory_updates",
            []
        ),
    )

# =========================================================
# WEEKLY UPDATE - COMPLETE
# =========================================================

@router.post(
    "/weekly/complete",
    response_model=WeeklyCompleteResponse
)
def complete_weekly_update(
    request: WeeklyCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # LOAD CONVERSATION
    # -----------------------------------------------------

    from app.repositories.conversation_repository import (
        ConversationRepository
    )

    conversation = ConversationRepository.get_by_id(
        db=db,
        conversation_id=request.conversation_id,
    )

    # -----------------------------------------------------
    # VALIDATE CONVERSATION
    # -----------------------------------------------------

    if not conversation:
        raise ValueError(
            "Weekly conversation not found"
        )

    if conversation.student_id != current_user.student_id:
        raise ValueError(
            "You are not authorized to access this conversation"
        )

    if conversation.conversation_type != "weekly_update":
        raise ValueError(
            "Conversation is not a weekly update"
        )

    # -----------------------------------------------------
    # LOAD ALL WEEKLY MESSAGES
    # -----------------------------------------------------

    messages = ConversationRepository.get_messages(
        db=db,
        conversation_id=request.conversation_id,
    )

    weekly_messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

    # -----------------------------------------------------
    # GENERATE WEEKLY SUMMARY
    # -----------------------------------------------------

    weekly_summary = (
        weekly_summary_service.generate_summary(
            recent_messages=weekly_messages,
            memory_updates=[],
        )
    )

    # -----------------------------------------------------
    # MODULE 2
    # -----------------------------------------------------

    # Module 2 is not connected yet.
    # This will become True once the actual Module 2
    # workflow is invoked.

    module2_triggered = False

    # -----------------------------------------------------
    # RETURN
    # -----------------------------------------------------

    return WeeklyCompleteResponse(
        conversation_id=request.conversation_id,
        weekly_update_summary=weekly_summary,
        module2_triggered=module2_triggered,
    )