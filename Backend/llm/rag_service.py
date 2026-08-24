"""
rag_service.py

Main Retrieval-Augmented Generation pipeline.

Flow:

Question
    ↓
Topic Extraction (or contextual-action bypass)
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

import re

from graph.graph_service import GraphService
from graph.learning_path import get_learning_path
from graph.recommendation import get_recommendations

from llm.topic_extractor import TopicExtractor
from llm.prompt_builder import PromptBuilder
from llm.answer_generator import generate_answer


# ==========================================================
# CONTEXTUAL ACTION DETECTION
#
# The frontend sends contextual actions (More Detail, Explain Simpler,
# etc.) as: "<topic> — <instruction>[, for <marks> marks]"
# e.g. "Binary Search — give a more detailed explanation, for 8 marks"
#
# Detecting this pattern lets us skip TopicExtractor entirely for these
# requests and go straight to build_follow_up_prompt() with the topic
# taken verbatim from the message — this is what makes "Binary Search"
# structurally unable to drift to an unrelated topic like "Detailed
# COCOMO", instead of just being less likely to.
# ==========================================================

CONTEXTUAL_PATTERN = re.compile(r"^(.+?)\s*—\s*(.+)$")

ACTION_PHRASE_MAP = {
    "explain it more simply": "simpler",
    "give a more detailed explanation": "more_detail",
    "create revision notes": "revision_notes",
    "generate viva questions": "viva_questions",
    "generate likely exam questions": "exam_questions",
    "create a short quiz": "short_quiz",
    "show the prerequisites": "prerequisites",
    "show related concepts": "related_concepts",
    "compare it with a similar concept": "compare",
}


def _detect_contextual_action(question: str):
    """
    Returns (topic_name, action, marks) if `question` matches the
    frontend's contextual-action format, otherwise None.
    """
    match = CONTEXTUAL_PATTERN.match(question.strip())
    if not match:
        return None

    topic_part = match.group(1).strip()
    instruction_part = match.group(2).strip()

    marks = None
    marks_match = re.search(r",\s*for\s+(\d+)\s*marks?\s*$", instruction_part, re.IGNORECASE)
    if marks_match:
        marks = int(marks_match.group(1))
        instruction_part = instruction_part[: marks_match.start()].strip()

    instruction_lower = instruction_part.lower().rstrip(".")
    action = ACTION_PHRASE_MAP.get(instruction_lower)
    if action is None:
        return None

    return topic_part, action, marks


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
        # STEP 0: CONTEXTUAL ACTION BYPASS
        #
        # If this matches the frontend's "<topic> — <instruction>" format,
        # skip TopicExtractor entirely and use the topic verbatim — this
        # is what makes it structurally impossible for a follow-up action
        # to drift to an unrelated topic.
        # ==========================================================

        contextual = _detect_contextual_action(question)

        if contextual is not None:
            topic_name, action, marks = contextual

            graph = GraphService.get_complete_response(topic_name)

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
            outgoing = graph.get("outgoing", [])
            incoming = graph.get("incoming", [])

            prompt = PromptBuilder.build_follow_up_prompt(
                topic_name=topic_name,
                action=action,
                marks=marks or 8,
                topic=node,
                outgoing=outgoing,
                incoming=incoming,
            )

            try:
                answer = generate_answer(
                    prompt,
                    num_predict=PromptBuilder.token_budget(marks or 8),
                )
            except Exception as error:
                print(f"RAG follow-up generation error: {error}")
                return {
                    "status": False,
                    "message": "Unable to generate the answer.",
                    "query": question,
                    "topic": topic_name,
                    "answer": "Unable to generate the answer at the moment. Please try again.",
                    "graph_context": outgoing,
                    "incoming": incoming,
                    "learning_path": [],
                    "recommendations": [],
                }

            try:
                learning_path = get_learning_path(topic_name)
            except Exception as error:
                print(f"Learning path error: {error}")
                learning_path = []

            try:
                recommendations = get_recommendations(topic_name)
            except Exception as error:
                print(f"Recommendation error: {error}")
                recommendations = []

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

        # ==========================================================
        # STEP 1: EXTRACT TOPIC (normal, non-contextual question)
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

            marks = PromptBuilder.detect_marks(question)

            answer = generate_answer(
                prompt,
                num_predict=PromptBuilder.token_budget(marks),
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
