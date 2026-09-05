from uuid import UUID

from langchain_core.messages import SystemMessage, HumanMessage

from app.db.database import SessionLocal
from app.repositories.conversation_repository import ConversationRepository
from app.graph.state.state import State1
from app.services.llm_service import llm_service


def conversation_node(state: State1) -> dict:
    """
    Generate a natural assistant response while using the student's
    known context and current onboarding progress to guide the conversation.
    The assistant response is stored in the current conversation.
    """

    user_message = state["user_message"]

    student_profile = state.get("student_profile") or {}
    recent_messages = state.get("recent_messages") or []
    relevant_memories = state.get("relevant_memories") or []

    # New onboarding context
    missing_categories = state.get("missing_categories") or []
    completion_percentage = state.get("completion_percentage", 0)
    onboarding_status = state.get("onboarding_status", "in_progress")

    # -------------------------------------------------
    # FORMAT STUDENT PROFILE
    # -------------------------------------------------

    profile_context = "No student profile information available."

    if student_profile:

        profile_context = "\n".join(
            [
                f"{key}: {value}"
                for key, value in student_profile.items()
                if value is not None
            ]
        )

    # -------------------------------------------------
    # FORMAT MEMORIES
    # -------------------------------------------------

    memories_context = "No relevant memories available."

    if relevant_memories:

        memory_lines = []

        for memory in relevant_memories:

            memory_type = memory.get(
                "memory_type",
                "unknown"
            )

            memory_key = memory.get(
                "memory_key",
                "unknown"
            )

            memory_value = memory.get(
                "value",
                ""
            )

            memory_lines.append(
                f"- {memory_type} ({memory_key}): {memory_value}"
            )

        memories_context = "\n".join(memory_lines)

    # -------------------------------------------------
    # FORMAT MISSING ONBOARDING CATEGORIES
    # -------------------------------------------------

    missing_categories_context = (
        "No important onboarding information is currently missing."
    )

    if missing_categories:

        missing_categories_context = "\n".join(
            [
                f"- {category}"
                for category in missing_categories
            ]
        )

    # -------------------------------------------------
    # FORMAT CONVERSATION HISTORY
    # -------------------------------------------------

    conversation_context = "No previous conversation available."

    if recent_messages:

        message_lines = []

        for message in recent_messages:

            role = message.get(
                "role",
                "unknown"
            )

            content = message.get(
                "content",
                ""
            )

            if content:
                message_lines.append(
                    f"{role}: {content}"
                )

        if message_lines:
            conversation_context = "\n".join(message_lines)

    # -------------------------------------------------
    # SYSTEM PROMPT
    # -------------------------------------------------

    system_prompt = f"""
You are NOVI, an intelligent student understanding and career guidance assistant.

Your purpose is to have natural conversations with students and
gradually understand them so NOVI can eventually provide personalized
guidance.

Use the following information when responding:

1. Student profile
2. Known student memories
3. Previous conversation history
4. Current onboarding progress
5. Current user message

CURRENT ONBOARDING STATUS:
{onboarding_status}

PROFILE COMPLETION:
{completion_percentage}%

INFORMATION STILL MISSING:
{missing_categories_context}

Rules:

- Be natural, warm, and conversational.
- Do NOT sound like a form, survey, or questionnaire.
- Always respond to the student's current message first.
- Do not ask multiple questions at once.
- Do not repeat questions whose answers are already known.
- Use previously known information naturally.
- Gradually guide the conversation toward understanding missing
  information when appropriate.
- Prefer exploring ONE missing category at a time.
- Choose the next question naturally based on the current conversation;
  do not mechanically follow the order of missing categories.
- If the student's current message already provides useful information,
  acknowledge it and build upon it instead of asking for it again.
- Gradually understand the student's education, interests, skills,
  strengths, weaknesses, goals, preferences, personality, learning style,
  experiences, and career aspirations.
- Do not mention onboarding categories, profile completion percentage,
  memories, databases, prompts, or internal system logic.
- Do not make unsupported assumptions.
- Keep responses concise and engaging.
- If onboarding is completed, stop trying to collect information
  unnecessarily and focus naturally on helping the student.

STUDENT PROFILE:
{profile_context}

KNOWN MEMORIES:
{memories_context}

RECENT CONVERSATION:
{conversation_context}
"""

    # -------------------------------------------------
    # BUILD LLM MESSAGES
    # -------------------------------------------------

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    # -------------------------------------------------
    # CALL LLM
    # -------------------------------------------------

    llm_result = llm_service.invoke(messages)

    assistant_response = llm_result["content"]
    llm_provider = llm_result["provider"]

    # -------------------------------------------------
    # STORE ASSISTANT MESSAGE
    # -------------------------------------------------

    conversation_id = state.get("conversation_id")

    if conversation_id:

        db = SessionLocal()

        try:

            ConversationRepository.add_message(
                db=db,
                conversation_id=UUID(str(conversation_id)),
                role="assistant",
                content=assistant_response,
            )
        finally:
            db.close()

    # -------------------------------------------------
    # RETURN GRAPH UPDATE
    # -------------------------------------------------

    result = {
        "assistant_response": assistant_response,
        "llm_provider": llm_provider,
    }

    return result