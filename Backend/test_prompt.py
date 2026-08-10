from graph_query import get_related_topics
from prompt_builder import build_prompt

topic = "Quick Sort"

graph_data = get_related_topics(topic)

prompt = build_prompt(topic, graph_data)

print(prompt)