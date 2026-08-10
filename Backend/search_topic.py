from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "Varshi1234")
)

topic = input("Enter topic: ")

query = """
MATCH (n)
WHERE toLower(n.label) CONTAINS toLower($topic)
RETURN n.label AS label,
       n.subject AS subject,
       n.type AS type
LIMIT 20
"""

with driver.session() as session:
    result = session.run(query, topic=topic)

    for record in result:
        print(record["label"],
              "|",
              record["subject"],
              "|",
              record["type"])

driver.close()