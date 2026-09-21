from neo4j_connection import driver

with driver.session() as session:
    result = session.run("""
    MATCH (n)
    RETURN n.label AS label
    LIMIT 10
    """)

    for record in result:
        print(record["label"])

driver.close()