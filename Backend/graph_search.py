from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "Varshi1234")
)

with driver.session() as session:
    result = session.run("""
    MATCH (n)
    RETURN n.label AS label
    LIMIT 10
    """)

    for record in result:
        print(record["label"])

driver.close()