"""
graph_query.py

Handles all communication with the Neo4j Knowledge Graph.
"""

from neo4j import GraphDatabase
from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)

# -------------------------------------------------------
# Neo4j Driver
# -------------------------------------------------------

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)

# -------------------------------------------------------
# Get Related Concepts
# -------------------------------------------------------

def get_related_topics(topic):
    """
    Returns all concepts directly connected to a topic.
    """

    query = """
    MATCH (n)

    WHERE toLower(COALESCE(n.label,n.name))
          = toLower($topic)

    MATCH (n)-[r]-(m)

    RETURN
        type(r) AS relation,
        COALESCE(m.label,m.name) AS concept

    ORDER BY relation
    """

    with driver.session() as session:

        result = session.run(
            query,
            topic=topic
        )

        return [
            {
                "relation": record["relation"],
                "related": record["concept"]
            }
            for record in result
        ]




# -------------------------------------------------------
# Close Driver
# -------------------------------------------------------

def close():

    driver.close()