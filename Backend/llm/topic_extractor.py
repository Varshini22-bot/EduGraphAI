"""
topic_extractor.py

Converts a natural-language question into a topic
that exists in the Neo4j Knowledge Graph.

Example:

"Explain Merge Sort"
        ↓
"Merge Sort"

"Tell me about Binary Search"
        ↓
"Binary Search"

"Quantum Computing"
        ↓
None
"""

import re

from graph.graph_service import GraphService


class TopicExtractor:

    @staticmethod
    def clean_question(question: str) -> str:

        question = question.strip()

        question = re.sub(
            r"\b("
            r"explain|"
            r"describe|"
            r"define|"
            r"what is|"
            r"what are|"
            r"tell me about|"
            r"how does|"
            r"how do|"
            r"give me information about|"
            r"information about"
            r")\b",
            "",
            question,
            flags=re.IGNORECASE
        )

        return question.strip(" ?.!,")


    @staticmethod
    def extract_topic(question: str):

        if not question or not question.strip():

            return None


        # --------------------------------------------------
        # Step 1: Clean the question
        # --------------------------------------------------

        cleaned_question = TopicExtractor.clean_question(
            question
        )


        # --------------------------------------------------
        # Step 2: Search complete topic
        # --------------------------------------------------

        results = GraphService.search(
            cleaned_question
        )


        if results:

            return results[0]["label"]


        # --------------------------------------------------
        # Step 3: Search individual words
        # --------------------------------------------------

        words = cleaned_question.split()


        for word in words:

            if len(word) < 3:

                continue


            results = GraphService.search(
                word
            )


            if results:

                return results[0]["label"]


        # --------------------------------------------------
        # Step 4: Unknown topic
        # --------------------------------------------------

        return None