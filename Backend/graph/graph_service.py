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
    # ==========================================================

    @staticmethod
    def get_complete_response(topic: str):

        node = GraphService.get_topic(topic)

        if node is None:

            return {

                "status": False,

                "message": "Topic not found",

                "node": None,

                "outgoing": [],

                "incoming": []

            }


        outgoing = GraphService.get_outgoing(topic)

        incoming = GraphService.get_incoming(topic)


        return {

            "status": True,

            "node": node,

            "outgoing": outgoing,

            "incoming": incoming

        }