"""
neo4j_client.py

Central Neo4j connection manager.

Every graph-related module should import the driver from here instead of
creating its own connection.
"""

from neo4j import GraphDatabase
from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
        )

    def close(self):
        self.driver.close()

    def get_session(self):
        return self.driver.session()


# Create one shared client
neo4j_client = Neo4jClient()


# Helper functions
def get_driver():
    return neo4j_client.driver


def get_session():
    return neo4j_client.get_session()