from llm.prompt_builder import PromptBuilder

topic = {
    "label": "Quick Sort",
    "type": "Algorithm",
    "subject": "ADA"
}

outgoing = [
    {
        "relationship": "uses",
        "target": "Divide and Conquer"
    },
    {
        "relationship": "is_a",
        "target": "Sorting Algorithm"
    }
]

incoming = [
    {
        "source": "Merge Sort",
        "relationship": "similar_to"
    }
]

prompt = PromptBuilder.build_prompt(
    "Explain Quick Sort",
    topic,
    outgoing,
    incoming
)

print(prompt)