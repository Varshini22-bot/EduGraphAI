from neo4j_connection import driver

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