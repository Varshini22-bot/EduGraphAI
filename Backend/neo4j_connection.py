import os
from neo4j import GraphDatabase

try:
    from config import (
        NEO4J_URI as URI,
        NEO4J_USERNAME as USERNAME,
        NEO4J_PASSWORD as PASSWORD,
    )
except ImportError:
    URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    PASSWORD = os.getenv("NEO4J_PASSWORD", "")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)