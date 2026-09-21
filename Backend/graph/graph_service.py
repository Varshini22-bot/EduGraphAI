"""
graph_service.py

Business logic for retrieving Knowledge Graph data from Neo4j.

This service is used by:
- Topic extraction
- RAG pipeline
- Learning path generation
- Recommendations
- API routes
"""

from graph.neo4j_client import get_session


class GraphService:

    _cached_topic_labels = None

    @classmethod
    def clear_topic_labels_cache(cls):
        cls._cached_topic_labels = None

    # ==========================================================
    # SEARCH TOPICS
    # ==========================================================

    @staticmethod
    def search(keyword: str):

        query = """
        MATCH (n)

        WHERE
            toLower(COALESCE(n.label, n.name))
            CONTAINS toLower($keyword)

        RETURN
            COALESCE(n.label, n.name) AS label,
            n.type AS type,
            n.subject AS subject

        LIMIT 20
        """

        with get_session() as session:

            result = session.run(
                query,
                keyword=keyword
            )

            return [
                {
                    "label": record["label"],
                    "type": record["type"],
                    "subject": record["subject"]
                }

                for record in result

                if record["label"] is not None
            ]


    # ==========================================================
    # ALL TOPIC LABELS
    #
    # PERF: returns every node label in one round trip so topic
    # extraction can match locally in Python instead of firing a
    # separate CONTAINS scan per word of the question (which cost
    # 1-5 round trips AND resolved the wrong topic - see
    # llm/topic_extractor.py for the details).
    #
    # This is global Knowledge Graph data, identical for every
    # user and containing no user data, so it is safe to cache in
    # memory and reuse across requests without any per-user isolation concern.
    # ==========================================================

    @staticmethod
    def get_all_topic_labels(force_refresh: bool = False):

        if GraphService._cached_topic_labels is not None and not force_refresh:
            return GraphService._cached_topic_labels

        query = """
        MATCH (n)

        WHERE
            COALESCE(n.label, n.name) IS NOT NULL

        RETURN DISTINCT
            COALESCE(n.label, n.name) AS label
        """

        with get_session() as session:

            result = session.run(query)

            labels = [
                record["label"]

                for record in result

                if record["label"] is not None
            ]

        GraphService._cached_topic_labels = labels

        return labels


    # ==========================================================
    # GET TOPIC NODE
    # ==========================================================

    @staticmethod
    def get_topic(topic: str):

        query = """
        MATCH (n)

        WHERE
            toLower(COALESCE(n.label, n.name))
            = toLower($topic)

        RETURN
            n
        """

        with get_session() as session:

            result = session.run(
                query,
                topic=topic
            )

            record = result.single()

            if record is None:

                return None

            node = record["n"]

            return dict(node)


    # ==========================================================
    # TOPIC EXISTS
    #
    # FIX: this method was called by api/graph_routes.py's
    # GET /graph/exists/{topic_name} route but never actually defined on
    # this class, causing an AttributeError (HTTP 500) on every call.
    # Minimal fix: reuse get_topic() rather than a new Cypher query, so
    # there's no duplicate topic-lookup logic.
    # ==========================================================

    @staticmethod
    def topic_exists(topic: str) -> bool:
        return GraphService.get_topic(topic) is not None


    # ==========================================================
    # GET OUTGOING RELATIONSHIPS
    # ==========================================================

    @staticmethod
    def get_outgoing(topic: str):

        query = """
        MATCH (n)-[r]->(m)

        WHERE
            toLower(COALESCE(n.label, n.name))
            = toLower($topic)

        RETURN
            type(r) AS relationship,

            COALESCE(m.label, m.name)
            AS target,

            m.type AS target_type,

            m.subject AS target_subject
        """

        with get_session() as session:

            result = session.run(
                query,
                topic=topic
            )

            return [

                {
                    "relationship": record["relationship"],

                    "target": record["target"],

                    "target_type": record["target_type"],

                    "target_subject": record["target_subject"]

                }

                for record in result

                if record["target"] is not None
            ]


    # ==========================================================
    # GET INCOMING RELATIONSHIPS
    # ==========================================================

    @staticmethod
    def get_incoming(topic: str):

        query = """
        MATCH (m)-[r]->(n)

        WHERE
            toLower(COALESCE(n.label, n.name))
            = toLower($topic)

        RETURN
            COALESCE(m.label, m.name)
            AS source,

            type(r) AS relationship,

            m.type AS source_type,

            m.subject AS source_subject
        """

        with get_session() as session:

            result = session.run(
                query,
                topic=topic
            )

            return [

                {
                    "source": record["source"],

                    "relationship": record["relationship"],

                    "source_type": record["source_type"],

                    "source_subject": record["source_subject"]

                }

                for record in result

                if record["source"] is not None
            ]


    # ==========================================================
    # GET NEIGHBOR TOPICS
    # ==========================================================

    @staticmethod
    def get_neighbors(topic: str):

        query = """
        MATCH (n)-[r]-(m)

        WHERE
            toLower(COALESCE(n.label, n.name))
            = toLower($topic)

        RETURN

            type(r) AS relationship,

            COALESCE(m.label, m.name)
            AS target,

            m.type AS target_type,

            m.subject AS target_subject
        """

        with get_session() as session:

            result = session.run(
                query,
                topic=topic
            )

            return [

                {
                    "relationship": record["relationship"],

                    "target": record["target"],

                    "target_type": record["target_type"],

                    "target_subject": record["target_subject"]

                }

                for record in result

                if record["target"] is not None
            ]


    # ==========================================================
    # COMPLETE TOPIC RESPONSE
    #
    # PERF: this used to call get_topic() + get_outgoing() +
    # get_incoming() = 3 separate Cypher statements in 3 separate
    # sessions, each one re-running the same
    # `toLower(COALESCE(n.label, n.name)) = toLower($topic)` scan
    # to find the SAME node. It is now a single round trip that
    # finds the node once and collects both directions from it.
    #
    # The three helper methods are deliberately kept - they are
    # each still used on their own by api/graph_routes.py.
    #
    # Return shape is unchanged, so /ask, /graph/topic and the
    # prompt builder all keep working exactly as before.
    # ==========================================================

    @staticmethod
    def get_complete_response(topic: str):

        query = """
        MATCH (n)

        WHERE
            toLower(COALESCE(n.label, n.name))
            = toLower($topic)

        WITH n LIMIT 1

        OPTIONAL MATCH (n)-[r_out]->(m)

        WITH n, collect(DISTINCT {
            relationship: type(r_out),
            target: COALESCE(m.label, m.name),
            target_type: m.type,
            target_subject: m.subject
        }) AS outgoing

        OPTIONAL MATCH (s)-[r_in]->(n)

        RETURN
            n,
            outgoing,
            collect(DISTINCT {
                source: COALESCE(s.label, s.name),
                relationship: type(r_in),
                source_type: s.type,
                source_subject: s.subject
            }) AS incoming
        """

        with get_session() as session:

            result = session.run(
                query,
                topic=topic
            )

            record = result.single()

        if record is None:

            return {

                "status": False,

                "message": "Topic not found",

                "node": None,

                "outgoing": [],

                "incoming": []

            }

        # A node with no relationships still produces one all-null
        # map from collect(DISTINCT ...) on an unmatched OPTIONAL
        # MATCH, so the null entries are filtered out here. This
        # mirrors the `if record[...] is not None` filtering the
        # three original helper methods already did.

        outgoing = [
            item

            for item in (record["outgoing"] or [])

            if item.get("target") is not None
        ]

        incoming = [
            item

            for item in (record["incoming"] or [])

            if item.get("source") is not None
        ]

        return {

            "status": True,

            "node": dict(record["n"]),

            "outgoing": outgoing,

            "incoming": incoming

        }
