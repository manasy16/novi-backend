import ast
import json
import re

from langchain_core.messages import SystemMessage, HumanMessage

from app.graph.state.state import State1
from app.services.llm_service import llm_service


def _clean_llm_json_response(response_content: str) -> str:
    """
    Extract the JSON object from an LLM response and remove
    markdown fences or surrounding text.
    """

    cleaned = str(response_content).strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned,
    )

    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]

    return cleaned.strip()


def _parse_memories_response(response_content: str) -> dict:
    """
    Parse LLM output robustly.
    """

    cleaned_response = _clean_llm_json_response(
        response_content
    )

    try:

        parsed_data = json.loads(
            cleaned_response
        )

        if isinstance(parsed_data, dict):
            return parsed_data

    except json.JSONDecodeError:
        pass

    try:

        parsed_data = ast.literal_eval(
            cleaned_response
        )

        if isinstance(parsed_data, dict):
            return parsed_data

    except (
        ValueError,
        SyntaxError,
    ):
        pass

    raise ValueError(
        "Could not parse memory extraction response "
        "as JSON or Python literal."
    )


def _validate_memory(memory: dict) -> dict | None:
    """
    Validate and normalize a single extracted memory.
    """

    if not isinstance(memory, dict):
        return None

    memory_type = memory.get(
        "memory_type"
    )

    memory_key = memory.get(
        "memory_key"
    )

    value = memory.get(
        "value"
    )

    if not memory_type or not memory_key or not value:
        return None

    confidence = memory.get(
        "confidence",
        0.8
    )

    try:
        confidence = float(
            confidence
        )
    except (
        TypeError,
        ValueError,
    ):
        confidence = 0.8

    confidence = max(
        0.0,
        min(
            1.0,
            confidence
        )
    )

    importance = memory.get(
        "importance",
        5
    )

    try:
        importance = int(
            importance
        )
    except (
        TypeError,
        ValueError,
    ):
        importance = 5

    importance = max(
        1,
        min(
            10,
            importance
        )
    )

    memory_key = str(
        memory_key
    ).strip().lower()

    memory_key = re.sub(
        r"[^a-z0-9]+",
        "_",
        memory_key,
    ).strip("_")

    return {
        "memory_type": str(
            memory_type
        ).strip().lower(),

        "memory_key": memory_key,

        "value": str(
            value
        ).strip(),

        "normalized_value": memory.get(
            "normalized_value"
        ),

        "confidence": confidence,

        "importance": importance,
    }


def memory_extractor_node(state: State1) -> dict:
    """
    Extract explicit, meaningful, long-term student
    information from the current user message.

    This node:

    - extracts facts
    - extracts activities
    - extracts projects
    - extracts achievements
    - extracts skills
    - extracts experiences
    - captures changes explicitly stated by the student

    This node does NOT:

    - infer personality
    - infer strengths from activities
    - infer career suitability
    - generate Career DNA
    - make career recommendations
    """

    user_message = state.get(
        "user_message",
        ""
    )

    if not user_message or not user_message.strip():

        return {
            "extracted_memories": []
        }

    existing_memories = state.get(
        "relevant_memories",
        []
    )

    existing_memory_context = []

    for memory in existing_memories:

        existing_memory_context.append(
            {
                "memory_type": memory.get(
                    "memory_type"
                ),

                "memory_key": memory.get(
                    "memory_key"
                ),

                "value": memory.get(
                    "value"
                ),
            }
        )

    system_prompt = """
You are the memory extraction system for NOVI,
an AI student understanding and career guidance platform.

Your job is to extract ONLY information that the
student explicitly states about themselves.

The information will be stored as long-term student
context and may later be analyzed by another module.

==================================================
ALLOWED MEMORY TYPES
==================================================

Use only these memory types:

education
interest
skill
career_goal
learning_preference

strength
weakness
experience
constraint
motivation

project
achievement
extracurricular
activity
hobby
goal


==================================================
CORE RULE
==================================================

EXTRACT FACTS.

DO NOT INFER.

If the student says:

"I play football."

Extract:

{
    "memory_type": "extracurricular",
    "memory_key": "football",
    "value": "Student plays football"
}

Do NOT extract:

"team_player"

Do NOT infer:

"Student has strong teamwork skills."


If the student says:

"I built a Python calculator."

Extract:

"project"

Do NOT infer:

"Student is highly technical."


If the student says:

"I find mathematics difficult."

You may extract:

"weakness"

because the student explicitly stated it.


==================================================
WEEKLY INFORMATION
==================================================

Weekly conversations may contain:

- things the student learned
- skills practiced
- projects built
- competitions
- clubs
- sports
- volunteering
- achievements
- failures
- difficulties
- experiences
- study habits
- learning activities
- goals
- changes from previous weeks

Extract these when explicitly stated.


==================================================
CHANGES
==================================================

If the student explicitly says something changed,
capture the NEW fact.

Example:

"I stopped learning Java and started learning Python."

Extract:

skill:
Python

Do not invent a reason for the change.


Example:

"I used to dislike coding but now I enjoy it."

Extract the current interest:

interest:
coding

You may also capture the change in the value if useful.


==================================================
EXPLICIT SELF-ASSESSMENTS
==================================================

If the student explicitly says:

"I'm good at Python."

This can be stored as:

strength:
Python

But do NOT convert other activities into strengths.

Example:

"I participated in a debate."

Does NOT mean:

"good communication."


==================================================
NO PERSONALITY INFERENCE
==================================================

Never create personality memories from behavior.

Do not infer:

- analytical
- creative
- disciplined
- hardworking
- introverted
- extroverted
- leader
- team player
- ambitious
- intelligent
- resilient

unless the student explicitly describes themselves
that way.

Even then, store only the explicit statement.


==================================================
NO CAREER INFERENCE
==================================================

Do not infer:

- career suitability
- career alignment
- Career DNA
- strengths
- personality
- future potential

Those are Module 2 responsibilities.


==================================================
DO NOT DUPLICATE EXISTING INFORMATION
==================================================

Existing memories are provided below.

If the current message repeats an existing fact
without adding anything new, do not extract it.

However, if the student provides a meaningful update,
extract the updated information.


==================================================
MEMORY KEY
==================================================

memory_key must:

- be short
- be descriptive
- use snake_case
- identify the specific fact


==================================================
CONFIDENCE
==================================================

Confidence represents how clearly the student stated
the information.

Explicit direct statement:
0.90 - 1.00

Clear but slightly ambiguous:
0.70 - 0.89

Never use confidence to represent personality
or career certainty.


==================================================
IMPORTANCE
==================================================

Importance represents how useful this information
is for understanding the student long-term.

Use:

8-10:
major career / education / long-term information

5-7:
useful ongoing information

1-4:
minor information


==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

Format:

{
    "memories": [
        {
            "memory_type": "skill",
            "memory_key": "python",
            "value": "Student knows Python",
            "normalized_value": "python",
            "confidence": 0.95,
            "importance": 8
        }
    ]
}

If nothing meaningful is present:

{
    "memories": []
}

No explanations.
No markdown.
No code fences.
"""

    human_prompt = f"""
EXISTING STUDENT MEMORIES:

{json.dumps(
    existing_memory_context,
    indent=2
)}


CURRENT STUDENT MESSAGE:

{user_message}
"""

    messages = [
        SystemMessage(
            content=system_prompt
        ),

        HumanMessage(
            content=human_prompt
        ),
    ]

    try:

        llm_result = llm_service.invoke(
            messages
        )

        response_content = llm_result[
            "content"
        ]

        extracted_data = (
            _parse_memories_response(
                response_content
            )
        )

        raw_memories = extracted_data.get(
            "memories",
            []
        )

        if not isinstance(
            raw_memories,
            list
        ):

            raise ValueError(
                "'memories' must be a list"
            )

        extracted_memories = []

        for memory in raw_memories:

            validated_memory = (
                _validate_memory(
                    memory
                )
            )

            if validated_memory:

                extracted_memories.append(
                    validated_memory
                )

        return {
            "extracted_memories":
                extracted_memories
        }

    except Exception as e:

        print(
            f"Memory extraction failed: "
            f"{type(e).__name__}: {e}"
        )

        return {
            "extracted_memories": []
        }