from neo4j_connection import driver

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