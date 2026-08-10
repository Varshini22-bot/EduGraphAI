from neo4j_connection import driver

def get_topic(topic):

    with driver.session() as session:

        query = """
        MATCH (n {label:$topic})-[r]-(m)
        RETURN n.label,
               type(r),
               m.label
        """

        result = session.run(
            query,
            topic=topic
        )

        return [record.data() for record in result]