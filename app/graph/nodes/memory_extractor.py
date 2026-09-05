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

    # Remove markdown code fences
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

    # Extract the outer JSON object if extra text exists
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]

    return cleaned.strip()


def _parse_memories_response(response_content: str) -> dict:
    """
    Parse LLM output robustly.

    First try valid JSON.
    If that fails, try Python literal parsing for responses such as:
    {'memories': [...]}
    """

    cleaned_response = _clean_llm_json_response(
        response_content
    )

    # First preference: strict JSON
    try:
        parsed_data = json.loads(cleaned_response)

        if isinstance(parsed_data, dict):
            return parsed_data

    except json.JSONDecodeError:
        pass

    # Fallback: Python-style dict/list returned by an LLM
    try:
        parsed_data = ast.literal_eval(cleaned_response)

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
    Invalid memories are ignored instead of breaking
    the entire extraction process.
    """

    if not isinstance(memory, dict):
        return None

    memory_type = memory.get("memory_type")
    memory_key = memory.get("memory_key")
    value = memory.get("value")

    # Required fields
    if not memory_type or not memory_key or not value:
        return None

    # Normalize confidence
    confidence = memory.get("confidence", 0.8)

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.8

    confidence = max(0.0, min(1.0, confidence))

    # Normalize importance
    importance = memory.get("importance", 5)

    try:
        importance = int(importance)
    except (TypeError, ValueError):
        importance = 5

    importance = max(1, min(10, importance))

    # Normalize memory key
    memory_key = str(memory_key).strip().lower()
    memory_key = re.sub(
        r"[^a-z0-9]+",
        "_",
        memory_key,
    ).strip("_")

    return {
        "memory_type": str(memory_type).strip().lower(),
        "memory_key": memory_key,
        "value": str(value).strip(),
        "normalized_value": memory.get(
            "normalized_value"
        ),
        "confidence": confidence,
        "importance": importance,
    }


def memory_extractor_node(state: State1) -> dict:
    """
    Extract meaningful long-term student information
    from the current user message.

    This node does NOT store anything in the database.
    It only identifies potential memories.
    """

    user_message = state.get("user_message", "")

    # Avoid unnecessary LLM calls
    if not user_message or not user_message.strip():
        return {
            "extracted_memories": [],
        }

    existing_memories = state.get(
        "relevant_memories",
        [],
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
You are a memory extraction system for a student understanding platform.

Your task is to analyze the student's message and extract ONLY
important information that would be useful to remember long-term.

Possible categories include:

- interest
- strength
- weakness
- goal
- career_goal
- skill
- preference
- education
- experience
- personality
- learning_style

Do NOT extract temporary information such as greetings,
casual statements, or questions with no personal information.

Return ONLY a valid JSON object.
Do not add explanations.
Do not add markdown.
Do not wrap the response in code fences.

The exact format is:

{
    "memories": [
        {
            "memory_type": "interest",
            "memory_key": "mathematics",
            "value": "Student enjoys mathematics",
            "normalized_value": "mathematics",
            "confidence": 0.9,
            "importance": 7
        }
    ]
}

Rules:

- Return {"memories": []} if there is nothing meaningful to remember.
- Do not duplicate information already known.
- memory_key must be short and snake_case.
- confidence must be between 0 and 1.
- importance must be between 1 and 10.
- Extract only factual information explicitly stated by the student.
- Do not infer information that the student did not state.
"""

    human_prompt = f"""
EXISTING STUDENT MEMORIES:

{json.dumps(existing_memory_context, indent=2)}

CURRENT STUDENT MESSAGE:

{user_message}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]

    try:

        llm_result = llm_service.invoke(messages)

        response_content = llm_result["content"]

        extracted_data = _parse_memories_response(
            response_content
        )

        raw_memories = extracted_data.get(
            "memories",
            [],
        )

        if not isinstance(raw_memories, list):
            raise ValueError(
                "'memories' must be a list"
            )

        extracted_memories = []

        for memory in raw_memories:

            validated_memory = _validate_memory(
                memory
            )

            if validated_memory:
                extracted_memories.append(
                    validated_memory
                )

        result = {
            "extracted_memories": extracted_memories,
        }

        return result

    except Exception as e:

        print(
            f"Memory extraction failed: "
            f"{type(e).__name__}: {e}"
        )

        return {
            "extracted_memories": [],
        }