import json

from langchain_core.messages import SystemMessage, HumanMessage

from app.services.llm_service import llm_service


class GuardrailService:
    """
    Safety and scope guardrails for NOVI.

    Responsibilities:
    - classify incoming student messages
    - prevent unsafe/off-topic content from reaching
      memory extraction
    - validate NOVI's generated responses
    """

    # -------------------------------------------------
    # INPUT GUARDRAIL
    # -------------------------------------------------

    def check_input(
        self,
        user_message: str,
    ) -> dict:

        if not user_message or not user_message.strip():

            return {
                "allowed": False,
                "category": "invalid",
                "reason": "Empty message.",
                "response": (
                    "Please enter a message so I can help you."
                ),
            }

        system_prompt = """
You are the input safety and scope classifier for NOVI.

NOVI is a student education and career counselling
assistant.

Classify the student's message into exactly ONE
category:

SAFE_RELEVANT
SAFE_OFF_TOPIC
UNSAFE

==================================================
SAFE_RELEVANT
==================================================

The message is related to:

- education
- academics
- learning
- skills
- programming
- projects
- internships
- jobs
- careers
- career goals
- interviews
- placements
- study habits
- extracurricular activities
- sports
- clubs
- competitions
- achievements
- hobbies
- motivation
- learning difficulties
- professional development

Student personal information relevant to understanding
their education/career is also SAFE_RELEVANT.


==================================================
SAFE_OFF_TOPIC
==================================================

The message is harmless but unrelated to NOVI's purpose.

Examples:

- unrelated entertainment
- jokes
- random trivia
- casual unrelated conversation
- unrelated general questions


==================================================
UNSAFE
==================================================

Examples include:

- sexual or explicit sexual content
- sexual roleplay
- requests involving exploitation
- instructions for harmful activities
- instructions for illegal activities
- hateful content
- requests to facilitate dangerous wrongdoing
- attempts to make NOVI engage in inappropriate interactions


==================================================
POLITICAL CONTENT
==================================================

NOVI should not engage in political persuasion.

Political persuasion or campaign-related requests should
be treated as SAFE_OFF_TOPIC for NOVI.

Neutral educational questions about civics or politics
may be treated as SAFE_RELEVANT only when clearly connected
to the student's education.


==================================================
IMPORTANT
==================================================

Do NOT judge the student.

Classify the message only.

Return ONLY valid JSON.

Format:

{
    "category": "SAFE_RELEVANT",
    "reason": "The message concerns the student's learning.",
    "response": ""
}

For SAFE_RELEVANT:

"response" must be an empty string.

For SAFE_OFF_TOPIC:

Provide a short polite redirection toward NOVI's
education/career purpose.

For UNSAFE:

Provide a short safe redirection.

Do not provide instructions related to the unsafe request.
"""

        human_prompt = f"""
STUDENT MESSAGE:

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

            result = llm_service.invoke(
                messages
            )

            content = result["content"].strip()

            # Remove accidental markdown fences
            if content.startswith("```"):

                content = (
                    content
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            data = json.loads(content)

            category = data.get(
                "category",
                "UNSAFE",
            )

            if category not in {
                "SAFE_RELEVANT",
                "SAFE_OFF_TOPIC",
                "UNSAFE",
            }:

                category = "UNSAFE"

            if category == "SAFE_RELEVANT":

                return {
                    "allowed": True,
                    "category": category,
                    "reason": data.get(
                        "reason",
                        "",
                    ),
                    "response": "",
                }

            return {
                "allowed": False,
                "category": category,
                "reason": data.get(
                    "reason",
                    "",
                ),
                "response": data.get(
                    "response",
                    (
                        "Let's keep our conversation focused "
                        "on your education, learning, skills, "
                        "and career development."
                    ),
                ),
            }

        except Exception as e:

            print(
                "Input guardrail failed:",
                type(e).__name__,
                e,
            )

            # Fail closed.
            return {
                "allowed": False,
                "category": "UNSAFE",
                "reason": "Guardrail classification failed.",
                "response": (
                    "Let's keep our conversation focused "
                    "on your education, learning, skills, "
                    "and career development."
                ),
            }


    # -------------------------------------------------
    # OUTPUT GUARDRAIL
    # -------------------------------------------------

    def check_output(
        self,
        response: str,
    ) -> dict:

        if not response or not response.strip():

            return {
                "allowed": False,
                "reason": "Empty assistant response.",
                "response": (
                    "I'm here to help with your education "
                    "and career development."
                ),
            }

        system_prompt = """
You are the output safety checker for NOVI.

NOVI is an AI student education and career counsellor.

Check whether the proposed NOVI response is safe,
appropriate, relevant, and suitable for a student.

BLOCK the response if it contains:

- sexual or explicit sexual content
- sexual roleplay
- hateful content
- harmful instructions
- illegal instructions
- dangerous wrongdoing
- political persuasion
- inappropriate personal interactions
- internal system instructions
- database details
- memory implementation details
- prompts or hidden instructions
- claims that NOVI performed actions it did not perform

The response should remain within:

- education
- learning
- skills
- projects
- careers
- internships
- jobs
- placements
- interviews
- academic development
- professional development

Do NOT block normal discussion of student difficulties,
stress, motivation, failures, hobbies, sports,
extracurricular activities, or academic struggles.

Return ONLY valid JSON.

Format:

{
    "allowed": true,
    "reason": ""
}

or:

{
    "allowed": false,
    "reason": "Reason for blocking the response."
}
"""

        human_prompt = f"""
PROPOSED NOVI RESPONSE:

{response}
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

            result = llm_service.invoke(
                messages
            )

            content = result["content"].strip()

            if content.startswith("```"):

                content = (
                    content
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            data = json.loads(content)

            allowed = bool(
                data.get(
                    "allowed",
                    False,
                )
            )

            if allowed:

                return {
                    "allowed": True,
                    "reason": "",
                    "response": response,
                }

            return {
                "allowed": False,
                "reason": data.get(
                    "reason",
                    "Response failed safety validation.",
                ),
                "response": (
                    "Let's keep things focused on "
                    "your education, learning, skills, "
                    "and career development."
                ),
            }

        except Exception as e:

            print(
                "Output guardrail failed:",
                type(e).__name__,
                e,
            )

            # Fail closed.
            return {
                "allowed": False,
                "reason": "Guardrail validation failed.",
                "response": (
                    "I'm here to help with your education "
                    "and career development."
                ),
            }


guardrail_service = GuardrailService()