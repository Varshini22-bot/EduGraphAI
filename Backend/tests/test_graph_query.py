from graph.graph_query import get_related_topics
from graph.learning_path import get_learning_path
from utils.stats import get_graph_statistics
from topic.load_topics import get_all_topics

print("Related Topics")
print("----------------")

print(
    get_related_topics(
        "Quick Sort"
    )
)

print()

print("Learning Path")
print("----------------")

print(
    get_learning_path(
        "Quick Sort"
    )
)

print()

print("Statistics")
print("----------------")

print(
    get_graph_statistics()
)

print()

print("Total Topics")

topics = get_all_topics()

print(len(topics))