import re
import time
from concurrent.futures import ThreadPoolExecutor

from graph.graph_service import GraphService
from graph.learning_path import get_learning_path
from graph.recommendation import get_recommendations

from llm.topic_extractor import TopicExtractor
from llm.prompt_builder import PromptBuilder
from llm.answer_generator import generate_answer

_EXECUTOR = ThreadPoolExecutor(max_workers=4)


def _fetch_recommendations_safe(topic_name: str) -> list:
    try:
        return get_recommendations(topic_name)
    except Exception as error:
        print(f"Recommendation error: {error}")
        return []


def _extract_learning_path(topic_name: str, outgoing: list) -> list:
    lp = [
        item["target"]
        for item in outgoing
        if item.get("relationship") == "USES" and item.get("target") is not None
    ]
    if lp:
        return lp
    try:
        return get_learning_path(topic_name)
    except Exception as error:
        print(f"Learning path error: {error}")
        return []


# ==========================================================
# CONTEXTUAL ACTION DETECTION
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


def _detect_contextual_action(question: str, context_topic: str = None):
    """
    Returns (topic_name, action, marks) if the question matches
    the frontend's contextual-action format or is a direct follow-up action
    referencing an active conversation topic.

    Example:
        Binary Search — give a more detailed explanation, for 8 marks
        Explain it more simply (with context_topic="Binary Search")
    """

    match = CONTEXTUAL_PATTERN.match(question.strip())

    if match:
        topic_part = match.group(1).strip()
        instruction_part = match.group(2).strip()
    elif context_topic and context_topic.strip():
        topic_part = context_topic.strip()
        instruction_part = question.strip()
    else:
        return None

    marks = None

    # The marks suffix may be a RANGE ("for 7-8 marks"), not just a single
    # number. The frontend's buildContextualActionQuery re-embeds whatever
    # the student originally wrote, and "7-8 marks" is one of the app's own
    # marks-preference labels, so ranges genuinely reach here.
    #
    # Before this accepted ranges, the whole pattern failed to match, which
    # made _detect_contextual_action return None and silently DROP the
    # follow-up action: clicking "Viva questions" produced a generic
    # explanation instead. The topic itself never drifted (TopicExtractor
    # still resolves it from the text), but the requested action was lost.
    marks_match = re.search(
        r",?\s*for\s+(\d+)(?:\s*[-–]\s*(\d+))?\s*marks?\s*$",
        instruction_part,
        re.IGNORECASE,
    )

    if marks_match:
        # A range is read as its UPPER bound, which is both what a student
        # means by "7-8 marks" and what PromptBuilder.detect_marks already
        # returns for the same phrasing - so the two stay consistent.
        # Taking the lower bound would shrink the answer depth instead.
        marks = int(marks_match.group(2) or marks_match.group(1))
        instruction_part = instruction_part[:marks_match.start()].strip()

    instruction_lower = instruction_part.lower().rstrip(".?!")

    action = ACTION_PHRASE_MAP.get(instruction_lower)

    if action is None:
        synonyms = {
            "explain more simply": "simpler",
            "simpler": "simpler",
            "make it simpler": "simpler",
            "explain simpler": "simpler",
            "more detail": "more_detail",
            "in detail": "more_detail",
            "explain in detail": "more_detail",
            "explain this in detail": "more_detail",
            "detailed explanation": "more_detail",
            "give revision notes": "revision_notes",
            "revision notes": "revision_notes",
            "make revision notes": "revision_notes",
            "viva questions": "viva_questions",
            "give viva questions": "viva_questions",
            "exam questions": "exam_questions",
            "likely exam questions": "exam_questions",
            "give likely exam questions": "exam_questions",
            "short quiz": "short_quiz",
            "give a quiz": "short_quiz",
            "quiz": "short_quiz",
            "prerequisites": "prerequisites",
            "show prerequisites": "prerequisites",
            "related concepts": "related_concepts",
            "related topics": "related_concepts",
            "compare": "compare",
            "compare with similar concept": "compare",
        }
        action = synonyms.get(instruction_lower)

    if action is None:
        return None

    return topic_part, action, marks


# ==========================================================
# RAG SERVICE
# ==========================================================

class RAGService:

    @staticmethod
    def answer(question: str, context_topic: str = None):

        # ==================================================
        # TOTAL TIMER
        # ==================================================

        total_start = time.perf_counter()

        # ==================================================
        # VALIDATE QUESTION
        # ==================================================

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

        print("\n" + "=" * 70)
        print("RAG REQUEST STARTED")
        print("=" * 70)
        print(f"Question: {question}")
        if context_topic:
            print(f"Context Topic: {context_topic}")

        # ==================================================
        # STEP 0: CONTEXTUAL ACTION BYPASS
        # ==================================================

        contextual = _detect_contextual_action(
            question,
            context_topic=context_topic,
        )

        if contextual is not None:

            topic_name, action, marks = contextual

            print("\n[CONTEXTUAL ACTION]")
            print(f"Topic: {topic_name}")
            print(f"Action: {action}")
            print(f"Marks: {marks}")

            # --------------------------------------------------
            # GRAPH RETRIEVAL TIMER
            # --------------------------------------------------

            graph_start = time.perf_counter()

            graph = GraphService.get_complete_response(topic_name)

            graph_time = time.perf_counter() - graph_start

            print(f"[TIMING] Graph retrieval: {graph_time:.2f} seconds")

            if not graph["status"]:

                total_time = time.perf_counter() - total_start

                print(
                    f"[TIMING] Total request time: "
                    f"{total_time:.2f} seconds"
                )

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

            # Launch recommendations concurrently while prompt and LLM execute
            rec_future = _EXECUTOR.submit(
                _fetch_recommendations_safe,
                topic_name
            )

            # --------------------------------------------------
            # PROMPT CONSTRUCTION TIMER
            # --------------------------------------------------

            prompt_start = time.perf_counter()

            prompt = PromptBuilder.build_follow_up_prompt(
                topic_name=topic_name,
                action=action,
                marks=marks or 8,
                topic=node,
                outgoing=outgoing,
                incoming=incoming,
            )

            prompt_time = time.perf_counter() - prompt_start

            print(
                f"[TIMING] Follow-up prompt construction: "
                f"{prompt_time:.2f} seconds"
            )

            # --------------------------------------------------
            # LLM TIMER
            # --------------------------------------------------

            llm_start = time.perf_counter()

            try:

                answer = generate_answer(
                    prompt,
                    num_predict=PromptBuilder.token_budget(marks or 8),
                )

            except Exception as error:

                llm_time = time.perf_counter() - llm_start

                print(
                    f"[TIMING] Ollama generation: "
                    f"{llm_time:.2f} seconds"
                )

                print(
                    f"RAG follow-up generation error: {error}"
                )

                total_time = time.perf_counter() - total_start

                print(
                    f"[TIMING] Total request time: "
                    f"{total_time:.2f} seconds"
                )

                return {
                    "status": False,
                    "message": "Unable to generate the answer.",
                    "query": question,
                    "topic": topic_name,
                    "answer": (
                        "Unable to generate the answer at the "
                        "moment. Please try again."
                    ),
                    "graph_context": outgoing,
                    "incoming": incoming,
                    "learning_path": [],
                    "recommendations": [],
                }

            llm_time = time.perf_counter() - llm_start

            print(
                f"[TIMING] Ollama generation: "
                f"{llm_time:.2f} seconds"
            )

            # --------------------------------------------------
            # LEARNING PATH & RECOMMENDATIONS
            # --------------------------------------------------

            lp_start = time.perf_counter()
            learning_path = _extract_learning_path(topic_name, outgoing)
            learning_path_time = time.perf_counter() - lp_start

            print(
                f"[TIMING] Learning path (derived): "
                f"{learning_path_time:.4f} seconds"
            )

            rec_start = time.perf_counter()
            try:
                recommendations = rec_future.result()
            except Exception as error:
                print(f"Recommendation future error: {error}")
                recommendations = []
            recommendations_time = time.perf_counter() - rec_start

            print(
                f"[TIMING] Recommendations (concurrent await): "
                f"{recommendations_time:.4f} seconds"
            )

            # --------------------------------------------------
            # TOTAL TIME
            # --------------------------------------------------

            total_time = time.perf_counter() - total_start

            print(
                f"[TIMING] TOTAL REQUEST: "
                f"{total_time:.2f} seconds"
            )

            print("=" * 70)
            print("RAG REQUEST COMPLETED")
            print("=" * 70 + "\n")

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

        # ==================================================
        # STEP 1: EXTRACT TOPIC
        # ==================================================

        topic_start = time.perf_counter()

        topic_name = TopicExtractor.extract_topic(
            question,
            context_topic=context_topic,
        )

        topic_time = time.perf_counter() - topic_start

        print("\n[TOPIC EXTRACTION]")
        print(f"Topic: {topic_name}")
        print(
            f"[TIMING] Topic extraction: "
            f"{topic_time:.2f} seconds"
        )

        # ==================================================
        # STEP 2: TOPIC NOT FOUND
        # ==================================================

        if topic_name is None:

            total_time = time.perf_counter() - total_start

            print(
                f"[TIMING] Total request time: "
                f"{total_time:.2f} seconds"
            )

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

        # ==================================================
        # STEP 3: RETRIEVE KNOWLEDGE GRAPH DATA
        # ==================================================

        graph_start = time.perf_counter()

        graph = GraphService.get_complete_response(
            topic_name
        )

        graph_time = time.perf_counter() - graph_start

        print(
            f"[TIMING] Graph retrieval: "
            f"{graph_time:.2f} seconds"
        )

        if not graph["status"]:

            total_time = time.perf_counter() - total_start

            print(
                f"[TIMING] Total request time: "
                f"{total_time:.2f} seconds"
            )

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

        # Launch recommendations concurrently while prompt and LLM execute
        rec_future = _EXECUTOR.submit(
            _fetch_recommendations_safe,
            topic_name
        )

        # ==================================================
        # STEP 4: BUILD GROUNDED PROMPT
        # ==================================================

        prompt_start = time.perf_counter()

        prompt = PromptBuilder.build_prompt(
            question=question,
            topic=node,
            outgoing=outgoing,
            incoming=incoming,
        )

        prompt_time = time.perf_counter() - prompt_start

        print(
            f"[TIMING] Prompt construction: "
            f"{prompt_time:.2f} seconds"
        )

        # ==================================================
        # STEP 5: GENERATE ANSWER
        # ==================================================

        marks = PromptBuilder.detect_marks(
            question
        )

        print(f"[ANSWER] Marks detected: {marks}")

        # --------------------------------------------------
        # OLLAMA TIMER
        # --------------------------------------------------

        llm_start = time.perf_counter()

        try:

            answer = generate_answer(
                prompt,
                num_predict=PromptBuilder.token_budget(
                    marks
                ),
            )

        except Exception as error:

            llm_time = time.perf_counter() - llm_start

            print(
                f"[TIMING] Ollama generation: "
                f"{llm_time:.2f} seconds"
            )

            print(
                f"RAG answer generation error: "
                f"{error}"
            )

            total_time = time.perf_counter() - total_start

            print(
                f"[TIMING] Total request time: "
                f"{total_time:.2f} seconds"
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

        llm_time = time.perf_counter() - llm_start

        print(
            f"[TIMING] Ollama generation: "
            f"{llm_time:.2f} seconds"
        )

        # ==================================================
        # STEP 6: LEARNING PATH & RECOMMENDATIONS
        # ==================================================

        lp_start = time.perf_counter()
        learning_path = _extract_learning_path(topic_name, outgoing)
        learning_path_time = time.perf_counter() - lp_start

        print(
            f"[TIMING] Learning path (derived): "
            f"{learning_path_time:.4f} seconds"
        )

        rec_start = time.perf_counter()
        try:
            recommendations = rec_future.result()
        except Exception as error:
            print(f"Recommendation future error: {error}")
            recommendations = []
        recommendations_time = time.perf_counter() - rec_start

        print(
            f"[TIMING] Recommendations (concurrent await): "
            f"{recommendations_time:.4f} seconds"
        )

        # ==================================================
        # STEP 8: TOTAL REQUEST TIME
        # ==================================================

        total_time = time.perf_counter() - total_start

        print("\n" + "=" * 70)
        print("RAG PERFORMANCE SUMMARY")
        print("=" * 70)

        print(
            f"Topic extraction       : "
            f"{topic_time:.2f} sec"
        )

        print(
            f"Graph retrieval        : "
            f"{graph_time:.2f} sec"
        )

        print(
            f"Prompt construction    : "
            f"{prompt_time:.2f} sec"
        )

        print(
            f"Ollama generation      : "
            f"{llm_time:.2f} sec"
        )

        print(
            f"Learning path          : "
            f"{learning_path_time:.2f} sec"
        )

        print(
            f"Recommendations        : "
            f"{recommendations_time:.2f} sec"
        )

        print("-" * 70)

        print(
            f"TOTAL                  : "
            f"{total_time:.2f} sec"
        )

        print("=" * 70 + "\n")

        # ==================================================
        # FINAL RESPONSE
        # ==================================================

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