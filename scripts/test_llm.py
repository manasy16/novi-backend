from langchain_core.messages import HumanMessage

from app.services.llm_service import llm_service


def test_llm_service():

    print("\n========== LLM SERVICE TEST ==========\n")

    messages = [
        HumanMessage(
            content="Say hello in one short sentence."
        )
    ]

    result = llm_service.invoke(messages)

    print("Provider:")
    print(result["provider"])

    print("\nContent:")
    print(result["content"])

    print("\nContent Type:")
    print(type(result["content"]))

    assert isinstance(
        result["content"],
        str,
    ), "LLM content must always be a string"

    print(
        "\n✓ LLM RESPONSE NORMALIZATION PASSED"
    )


if __name__ == "__main__":
    test_llm_service()