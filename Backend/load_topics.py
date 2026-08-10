from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "Varshi1234")
)

def get_all_topics():

    query = """
    MATCH (n)
    WHERE n.label IS NOT NULL
    RETURN DISTINCT n.label AS topic
    ORDER BY topic
    """

    with driver.session() as session:

        result = session.run(query)

        topics = [
            record["topic"]
            for record in result
        ]

    return topics


if __name__ == "__main__":

    topics = get_all_topics()

    print(f"Total Topics: {len(topics)}\n")

    for topic in topics:
        print(topic)