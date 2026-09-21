from neo4j_connection import driver

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