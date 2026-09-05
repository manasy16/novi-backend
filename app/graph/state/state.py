from typing import TypedDict, Optional, List, Dict, Any
from uuid import UUID


class State1(TypedDict, total=False):
    """
    Shared state for the Module 1 LangGraph workflow.
    """

    # -------------------------------------------------
    # Identity from Auth module
    # -------------------------------------------------

    external_student_id: str
    student_id: UUID

    # -------------------------------------------------
    # Conversation
    # -------------------------------------------------

    conversation_id: Optional[UUID]
    conversation_type: str

    # -------------------------------------------------
    # Incoming message
    # -------------------------------------------------

    user_message: str

    # -------------------------------------------------
    # Loaded context
    # -------------------------------------------------

    student_profile: Dict[str, Any]
    recent_messages: List[Dict[str, Any]]
    relevant_memories: List[Dict[str, Any]]

    # -------------------------------------------------
    # Conversation output
    # -------------------------------------------------

    assistant_response: str
    llm_provider: str

    # -------------------------------------------------
    # Memory extraction
    # -------------------------------------------------

    extracted_memories: List[Dict[str, Any]]

    # -------------------------------------------------
    # Memory persistence results
    # -------------------------------------------------

    memory_updates: List[Dict[str, Any]]

    # -------------------------------------------------
    # Onboarding tracking
    # -------------------------------------------------

    onboarding_status: Optional[str]

    onboarding_profile: Optional[Dict[str, Any]]

    known_categories: List[str]

    completed_categories: List[str]

    missing_categories: List[str]

    completion_percentage: int

    # -------------------------------------------------
    # Future module integration
    # -------------------------------------------------

    module2_triggered: bool