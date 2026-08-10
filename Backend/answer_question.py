from graph_query import get_related_topics
from prompt_builder import build_prompt
from llm import generate_answer

topic = input("Topic: ")

graph_data = get_related_topics(topic)

print("\nRetrieved Graph Context:\n")

for item in graph_data:
    print(f"{item['relation']} -> {item['related']}")

prompt = build_prompt(topic, graph_data)

answer = generate_answer(prompt)

print("\nAnswer:\n")
print(answer)