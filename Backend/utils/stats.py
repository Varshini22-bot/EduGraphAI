from graph.graph_query import driver


def get_stats():

    with driver.session() as session:

        node_query = """
        MATCH (n)
        RETURN count(n) AS count
        """

        relationship_query = """
        MATCH ()-[r]->()
        RETURN count(r) AS count
        """

        nodes = session.run(node_query).single()["count"]

        relationships = session.run(
            relationship_query
        ).single()["count"]

    return nodes, relationships