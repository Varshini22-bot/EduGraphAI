from graph.graph_query import driver


def get_all_topics():

    query = """
    MATCH (n)
    WHERE n.label IS NOT NULL
    RETURN DISTINCT n.label AS topic
    ORDER BY topic
    """

    with driver.session() as session:

        result = session.run(query)

        return [
            record["topic"]
            for record in result
        ]


if __name__ == "__main__":

    topics = get_all_topics()

    print(f"Total Topics: {len(topics)}")

    for topic in topics:
        print(topic)