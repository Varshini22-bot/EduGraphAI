from neo4j import GraphDatabase

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD
)

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def get_graph(topic: str):

    query = """
    MATCH (n:Concept)-[r]-(m:Concept)

    WHERE toLower(n.label)=toLower($topic)

    RETURN
        n.label AS source,
        type(r) AS relation,
        m.label AS target
    """

    nodes = {}
    links = []

    with driver.session() as session:

        result = session.run(query, topic=topic)

        for record in result:

            source = record["source"]
            target = record["target"]

            nodes[source] = {
                "id": source,
                "label": source
            }

            nodes[target] = {
                "id": target,
                "label": target
            }

            links.append({
                "source": source,
                "target": target,
                "label": record["relation"]
            })

    return {
        "nodes": list(nodes.values()),
        "links": links
    }