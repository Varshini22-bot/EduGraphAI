from graph.neo4j_client import get_session


def get_learning_path(topic):

    query = """
    MATCH (n)

    WHERE toLower(COALESCE(n.label, n.name))
          = toLower($topic)

    WITH n LIMIT 1

    MATCH (n)-[:USES]->(m)

    RETURN COALESCE(m.label, m.name) AS concept
    """

    with get_session() as session:

        result = session.run(
            query,
            topic=topic
        )

        return [
            record["concept"]
            for record in result
            if record["concept"] is not None
        ]