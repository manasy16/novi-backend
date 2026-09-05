from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


class LLMService:

    def __init__(self):

        self.providers = [
            (
                "groq",
                ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model="qwen/qwen3.8-27b",
                    temperature=0.7,
                ),
            ),
            (
                "mistral",
                ChatMistralAI(
                    api_key=settings.MISTRAL_API_KEY,
                    model="mistral-small-latest",
                    temperature=0.7,
                ),
            ),
            (
                "gemini",
                ChatGoogleGenerativeAI(
                    google_api_key=settings.GOOGLE_API_KEY,
                    model="gemini-2.0-flash",
                    temperature=0.7,
                ),
            ),
        ]

    def _extract_text_content(self, content) -> str:
        """
        Normalize different provider response formats
        into a plain text string.
        """

        # Normal string response
        if isinstance(content, str):
            return content

        # Gemini or other providers may return a dict
        if isinstance(content, dict):

            if "text" in content:
                return str(content["text"])

            return str(content)

        # Some providers may return a list of content blocks
        if isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, str):
                    text_parts.append(item)

                elif isinstance(item, dict):

                    if item.get("type") == "text":
                        text = item.get("text")

                        if text:
                            text_parts.append(str(text))

                    elif "text" in item:
                        text_parts.append(
                            str(item["text"])
                        )

            if text_parts:
                return "\n".join(text_parts)

            return str(content)

        # Fallback
        return str(content)

    def invoke(self, messages: list[BaseMessage]) -> dict:

        errors = []

        for provider_name, llm in self.providers:

            try:

                response = llm.invoke(messages)

                content = self._extract_text_content(
                    response.content
                )

                return {
                    "content": content,
                    "provider": provider_name,
                }

            except Exception as e:

                errors.append(
                    f"{provider_name}: {str(e)}"
                )

        raise RuntimeError(
            "All LLM providers failed. "
            + " | ".join(errors)
        )


llm_service = LLMService()