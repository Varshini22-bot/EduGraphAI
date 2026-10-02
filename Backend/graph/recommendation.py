from graph.neo4j_client import get_session


def get_recommendations(topic):

    query = """
    MATCH (n)

    WHERE toLower(COALESCE(n.label, n.name))
          = toLower($topic)

    WITH n LIMIT 1

    MATCH (n)-[:USES|RELATED_TO|CONTAINS]-(m)

    OPTIONAL MATCH (m)-[:USES|RELATED_TO|CONTAINS]-(x)

    WHERE x IS NOT NULL
      AND x <> n

    WITH
        COLLECT(DISTINCT COALESCE(m.label, m.name))
        +
        COLLECT(DISTINCT COALESCE(x.label, x.name))
        AS recommendations

    UNWIND recommendations AS rec

    WITH DISTINCT rec

    WHERE rec IS NOT NULL

    RETURN rec

    LIMIT 10
    """

    try:
        with get_session() as session:
            result = session.run(
                query,
                topic=topic
            )
            return [
                record["rec"]
                for record in result
                if record["rec"] is not None
            ]
    except Exception:
        from graph.static_graph_store import StaticGraphStore
        neighbors = StaticGraphStore.get_neighbors(topic)
        recs = []
        for n in neighbors:
            tgt = n.get("target") or n.get("source")
            if tgt and tgt.lower() != str(topic).lower() and tgt not in recs:
                recs.append(tgt)
        return recs[:10]