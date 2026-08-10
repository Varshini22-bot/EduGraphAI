"""
rag_service.py

Main Retrieval-Augmented Generation pipeline.

Flow:

Question
    ↓
Topic Extraction
    ↓
Knowledge Graph Retrieval
    ↓
Prompt Construction
    ↓
LLM Answer Generation
    ↓
Learning Path / Recommendations
    ↓
Final Response
"""

from graph.graph_service import GraphService
from graph.learning_path import get_learning_path
from graph.recommendation import get_recommendations

from llm.topic_extractor import TopicExtractor
from llm.prompt_builder import PromptBuilder
from llm.answer_generator import generate_answer


class RAGService:

    @staticmethod
    def answer(question: str):

        # ==========================================================
        # VALIDATE QUESTION
        # ==========================================================

        question = (question or "").strip()

        if not question:

            return {
                "status": False,
                "message": "Please enter a valid question or topic.",
                "query": "",
                "topic": None,
                "answer": "Please enter a valid question or topic.",
                "graph_context": [],
                "incoming": [],
                "learning_path": [],
                "recommendations": [],
            }

        # ==========================================================
        # STEP 1: EXTRACT TOPIC
        # ==========================================================

        topic_name = (
            TopicExtractor.extract_topic(
                question
            )
        )

        # ==========================================================
        # STEP 2: TOPIC NOT FOUND
        # ==========================================================

        if topic_name is None:

            return {
                "status": False,
                "message": "Topic not found in the Knowledge Graph.",
                "query": question,
                "topic": None,
                "answer": (
                    "The requested topic could not be identified "
                    "in the Knowledge Graph."
                ),
                "graph_context": [],
                "incoming": [],
                "learning_path": [],
                "recommendations": [],
            }

        # ==========================================================
        # STEP 3: RETRIEVE KNOWLEDGE GRAPH DATA
        # ==========================================================

        graph = (
            GraphService.get_complete_response(
                topic_name
            )
        )

        if not graph["status"]:

            return {
                "status": False,
                "message": "Topic not found in the Knowledge Graph.",
                "query": question,
                "topic": topic_name,
                "answer": (
                    f"No reliable Knowledge Graph information "
                    f"was found for '{topic_name}'."
                ),
                "graph_context": [],
                "incoming": [],
                "learning_path": [],
                "recommendations": [],
            }

        node = graph["node"]

        outgoing = graph.get(
            "outgoing",
            []
        )

        incoming = graph.get(
            "incoming",
            []
        )

        # ==========================================================
        # STEP 4: BUILD GROUNDED PROMPT
        # ==========================================================

        prompt = (
            PromptBuilder.build_prompt(
                question=question,
                topic=node,
                outgoing=outgoing,
                incoming=incoming,
            )
        )

        # ==========================================================
        # STEP 5: GENERATE ANSWER
        # ==========================================================

        try:

            answer = generate_answer(
                prompt
            )

        except Exception as error:

            print(
                f"RAG answer generation error: {error}"
            )

            return {
                "status": False,
                "message": "Unable to generate the answer.",
                "query": question,
                "topic": topic_name,
                "answer": (
                    "Unable to generate the answer "
                    "at the moment. Please try again."
                ),
                "graph_context": outgoing,
                "incoming": incoming,
                "learning_path": [],
                "recommendations": [],
            }

        # ==========================================================
        # STEP 6: LEARNING PATH
        # ==========================================================

        try:

            learning_path = (
                get_learning_path(
                    topic_name
                )
            )

        except Exception as error:

            print(
                f"Learning path error: {error}"
            )

            learning_path = []

        # ==========================================================
        # STEP 7: RECOMMENDATIONS
        # ==========================================================

        try:

            recommendations = (
                get_recommendations(
                    topic_name
                )
            )

        except Exception as error:

            print(
                f"Recommendation error: {error}"
            )

            recommendations = []

        # ==========================================================
        # STEP 8: FINAL RESPONSE
        # ==========================================================

        return {
            "status": True,
            "message": "Answer generated successfully.",
            "query": question,
            "topic": topic_name,
            "answer": answer,
            "graph_context": outgoing,
            "incoming": incoming,
            "learning_path": learning_path,
            "recommendations": recommendations,
        }