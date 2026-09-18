from langchain_core.messages import SystemMessage, HumanMessage

from app.graph.state.state import State1
from app.services.llm_service import llm_service
from app.db.database import SessionLocal
from app.repositories.conversation_repository import ConversationRepository


def weekly_conversation_node(state: State1):

    user_message = state.get("user_message", "").strip()

    recent_messages = state.get("recent_messages", [])
    relevant_memories = state.get("relevant_memories", [])

    # ---------------------------------------------------------
    # BUILD STUDENT MEMORY CONTEXT
    # ---------------------------------------------------------

    memory_context = ""

    if relevant_memories:

        memory_lines = []

        for memory in relevant_memories:

            memory_lines.append(
                f"- {memory.get('memory_type')}: "
                f"{memory.get('value')}"
            )

        memory_context = "\n".join(memory_lines)

    # ---------------------------------------------------------
    # BUILD CONVERSATION HISTORY
    # ---------------------------------------------------------

    conversation_history = []

    if recent_messages:

        for message in recent_messages:

            role = message.get("role")

            content = message.get("content", "")

            if role == "user":

                conversation_history.append(
                    HumanMessage(content=content)
                )

            elif role == "assistant":

                conversation_history.append(
                    SystemMessage(
                        content=f"NOVI previously said: {content}"
                    )
                )

    # ---------------------------------------------------------
    # SYSTEM PROMPT
    # ---------------------------------------------------------

    system_prompt = """
You are NOVI, an AI student career companion.

This is a WEEKLY CHECK-IN conversation.

Your job is to have a natural conversation with the student
about what they worked on, learned, experienced, struggled with,
or achieved during the week.

IMPORTANT RULES:

1. Do NOT treat this as onboarding.
2. Do NOT use the onboarding checklist.
3. Do NOT ask questions from a fixed checklist.
4. Follow what the student is talking about naturally.
5. Ask at most ONE useful follow-up question at a time.
6. Encourage the student to share concrete experiences.

You may discuss:

- academics
- programming
- skills
- projects
- internships
- competitions
- extracurricular activities
- sports
- clubs
- achievements
- difficulties
- learning habits
- goals

7. Do not invent facts about the student.
8. Do not make unsupported personality or career conclusions.
9. Do not generate a Career DNA profile here.
10. Keep responses concise and conversational.
11. If the student provides useful information, acknowledge it
    and naturally continue the conversation.
"""

    # ---------------------------------------------------------
    # BUILD CURRENT USER PROMPT
    # ---------------------------------------------------------

    user_prompt = f"""
STUDENT'S EXISTING MEMORY:

{memory_context}


CURRENT WEEKLY CONVERSATION:

The previous conversation history is provided in the messages.


STUDENT'S NEW MESSAGE:

{user_message}


Respond naturally to the student's message.

Ask only ONE follow-up question if useful.
"""

    # ---------------------------------------------------------
    # BUILD LLM MESSAGES
    # ---------------------------------------------------------

    messages = [

        SystemMessage(
            content=system_prompt
        ),

        *conversation_history,

        HumanMessage(
            content=user_prompt
        ),
    ]

    # ---------------------------------------------------------
    # CALL EXISTING LLM SERVICE
    # ---------------------------------------------------------

    response = llm_service.invoke(
        messages
    )

    assistant_response = response.get(
        "content",
        ""
    )

    provider = response.get(
        "provider",
        "unknown"
    )

    # ---------------------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # ---------------------------------------------------------

    conversation_id = state.get(
        "conversation_id"
    )

    if conversation_id:

        db = SessionLocal()

        try:

            ConversationRepository.add_message(
                db=db,
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_response,
            )

        finally:

            db.close()

    # ---------------------------------------------------------
    # RETURN
    # ---------------------------------------------------------

    return {

        "assistant_response":
            assistant_response,

        "llm_provider":
            provider,
    }