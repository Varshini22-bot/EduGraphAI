from graph.graph_service import GraphService

topic = "Quick Sort"

print("--------------------------------")

print(GraphService.topic_exists(topic))

print("--------------------------------")

print(GraphService.get_node(topic))

print("--------------------------------")

print(GraphService.get_neighbors(topic))

print("--------------------------------")

print(GraphService.get_incoming(topic))

print("--------------------------------")

print(GraphService.search("sort"))

print("--------------------------------")

print(GraphService.get_complete_response(topic))