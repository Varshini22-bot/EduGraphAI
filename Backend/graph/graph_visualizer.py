from pyvis.network import Network
from graph_query import get_related_topics


def generate_graph(topic):

    graph = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        directed=True
    )

    # Main topic node
    graph.add_node(
        topic,
        label=topic,
        color="#ff6b6b",
        size=30
    )

    relations = get_related_topics(topic)

    for item in relations:

        related = item["related"]
        relation = item["relation"]

        graph.add_node(
            related,
            label=related,
            color="#4dabf7",
            size=20
        )

        graph.add_edge(
            topic,
            related,
            label=relation
        )

    graph.repulsion(
        node_distance=220,
        central_gravity=0.3,
        spring_length=200,
        spring_strength=0.05
    )

    graph.save_graph("graph.html")