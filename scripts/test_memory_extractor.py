from app.graph.nodes.memory_extractor import (
    memory_extractor_node,
)


def test_memory_extractor():

    print("\n========== MEMORY EXTRACTOR TEST ==========\n")

    state = {
        "user_message": (
            "I am a second year B.Tech Computer Science student. "
            "I enjoy mathematics and logical problem solving. "
            "I know Python and want to become a machine learning engineer."
        ),
        "relevant_memories": [],
    }

    result = memory_extractor_node(state)

    print("EXTRACTED MEMORIES:\n")

    for memory in result["extracted_memories"]:
        print(memory)

    print(
        f"\nTotal extracted: "
        f"{len(result['extracted_memories'])}"
    )


if __name__ == "__main__":
    test_memory_extractor()