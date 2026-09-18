from langchain_core.messages import SystemMessage, HumanMessage

from app.services.llm_service import llm_service


class WeeklySummaryService:

    def generate_summary(
        self,
        recent_messages: list[dict],
        memory_updates: list[dict],
    ) -> dict:

        # -----------------------------------------------------
        # CONVERSATION
        # -----------------------------------------------------

        conversation_lines = []

        for message in recent_messages:

            role = message.get("role", "unknown")
            content = message.get("content", "")

            conversation_lines.append(
                f"{role}: {content}"
            )

        conversation_text = "\n".join(
            conversation_lines
        )

        # -----------------------------------------------------
        # MEMORY UPDATES
        # -----------------------------------------------------

        memory_lines = []

        for memory in memory_updates:

            action = memory.get("action", "")
            memory_type = memory.get("memory_type", "")
            memory_key = memory.get("memory_key", "")
            value = memory.get("value", "")

            memory_lines.append(
                f"- {action}: "
                f"{memory_type} / "
                f"{memory_key}: "
                f"{value}"
            )

        memory_text = "\n".join(
            memory_lines
        )

        # -----------------------------------------------------
        # SUMMARY PROMPT
        # -----------------------------------------------------

        system_prompt = """
You are NOVI's weekly update summarization service.

Create a factual summary of what the student shared
during this weekly check-in.

Your job is to summarize information, NOT interpret it.

Return ONLY valid JSON in this structure:

{
    "summary": "short factual summary",
    "new_information": [
        "fact 1",
        "fact 2"
    ],
    "changes": [
        "change 1",
        "change 2"
    ]
}

RULES:

1. Only use information explicitly present in the conversation
   or memory updates.
2. Do not invent information.
3. Do not infer personality traits.
4. Do not generate Career DNA.
5. Do not recommend careers.
6. Do not score the student.
7. "new_information" should contain meaningful new facts
   learned during this week.
8. "changes" should contain explicit changes mentioned by
   the student compared with their previous situation.
9. If there are no explicit changes, return an empty list.
10. Keep the summary concise.
"""

        # -----------------------------------------------------
        # USER PROMPT
        # -----------------------------------------------------

        user_prompt = f"""
WEEKLY CONVERSATION:

{conversation_text}


MEMORY UPDATES:

{memory_text}


Create the weekly summary.
Return ONLY valid JSON.
"""

        messages = [
            SystemMessage(
                content=system_prompt
            ),
            HumanMessage(
                content=user_prompt
            ),
        ]

        # -----------------------------------------------------
        # CALL LLM
        # -----------------------------------------------------

        response = llm_service.invoke(
            messages
        )

        content = response.get(
            "content",
            ""
        )

        # -----------------------------------------------------
        # PARSE JSON
        # -----------------------------------------------------

        import json

        try:

            result = json.loads(
                content
            )

        except json.JSONDecodeError:

            # Try extracting JSON from markdown
            cleaned = content.strip()

            if cleaned.startswith("```"):
                cleaned = (
                    cleaned
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            try:

                result = json.loads(
                    cleaned
                )

            except json.JSONDecodeError:

                result = {
                    "summary": content,
                    "new_information": [],
                    "changes": [],
                }

        # -----------------------------------------------------
        # ENSURE EXPECTED STRUCTURE
        # -----------------------------------------------------

        return {
            "summary": result.get(
                "summary",
                ""
            ),

            "new_information": result.get(
                "new_information",
                []
            ),

            "changes": result.get(
                "changes",
                []
            ),
        }


weekly_summary_service = WeeklySummaryService()