from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "Varshi1234")
)

topic = input("Topic: ")

query = """
MATCH (n)-[r]-(m)
WHERE toLower(n.label)=toLower($topic)

RETURN
COALESCE(m.label,m.name) AS related,
type(r) AS relation
"""

with driver.session() as session:
    result = session.run(query, topic=topic)

    print("\nRelated Topics:\n")

    found = False

    for record in result:
        if record["related"]:
            print(record["related"])
            found = True

    if not found:
        print("No related topics found.")

driver.close()