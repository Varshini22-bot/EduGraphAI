"""
graph_query.py

Handles all communication with the Neo4j Knowledge Graph.
"""

from neo4j import GraphDatabase
from config import *

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
# Get Learning Path
# -------------------------------------------------------

def get_learning_path(topic):
    """
    Returns concepts connected using USES relationship.
    """

    query = """
    MATCH (n)

    WHERE toLower(COALESCE(n.label,n.name))
          = toLower($topic)

    MATCH (n)-[:USES]->(m)

    RETURN
        COALESCE(m.label,m.name) AS concept
    """

    with driver.session() as session:

        result = session.run(
            query,
            topic=topic
        )

        return [
            record["concept"]
            for record in result
        ]

# -------------------------------------------------------
# Graph Statistics
# -------------------------------------------------------

def get_graph_statistics():

    with driver.session() as session:

        nodes = session.run(
            "MATCH (n) RETURN count(n) AS total"
        ).single()["total"]

        relationships = session.run(
            "MATCH ()-[r]->() RETURN count(r) AS total"
        ).single()["total"]

    return nodes, relationships


# -------------------------------------------------------
# Get All Topics
# -------------------------------------------------------

def get_all_topics():

    query = """
    MATCH (n)

    RETURN DISTINCT
    COALESCE(n.label,n.name) AS topic

    ORDER BY topic
    """

    with driver.session() as session:

        result = session.run(query)

        return [
            record["topic"]
            for record in result
        ]


# -------------------------------------------------------
# Close Driver
# -------------------------------------------------------

def close():

    driver.close()