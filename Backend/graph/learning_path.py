from graph.graph_query import driver


def get_learning_path(topic):

    query = """
    MATCH (n)

    WHERE toLower(COALESCE(n.label, n.name))
          = toLower($topic)

    MATCH (n)-[:USES]->(m)

    RETURN COALESCE(m.label, m.name) AS concept
    """

    with driver.session() as session:

        result = session.run(
            query,
            topic=topic
        )

        return [
            record["concept"]
            for record in result
            if record["concept"] is not None
        ]