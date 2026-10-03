"""
Backend/evaluation/baselines/kg_rag_runner.py

EduGraphAI Knowledge-Graph-RAG Runner for Research Evaluation.

Wraps the existing verified EduGraphAI RAGService (Backend/llm/rag_service.py)
without duplicating or modifying the production pipeline.
"""

import os
import sys
import time
from typing import Any, Dict, Optional

# Ensure Backend directory is in sys.path
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from llm.rag_service import RAGService
from config import LLM_MODEL, LLM_PROVIDER


class KGRAGRunner:
    """
    Knowledge Graph-grounded RAG runner.
    Delegates directly to EduGraphAI's existing RAGService to perform:
    - Intent and marks detection
    - Canonical entity resolution via TopicExtractor
    - 1-hop / 2-hop graph traversal and relationship retrieval via GraphService
    - Knowledge-grounded academic answer generation via PromptBuilder
    """

    SYSTEM_NAME = "kg_rag"

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or LLM_MODEL
        self.provider = LLM_PROVIDER

    def run(self, question: str, context_topic: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Executes EduGraphAI's Knowledge Graph-RAG pipeline for a given question.

        Args:
            question: Natural language question.
            context_topic: Optional existing conversation topic for follow-up turns.

        Returns:
            Dict containing system identifier, answer text, structured retrieved graph context,
            retrieval_hit flag, and latency in seconds.
        """
        start_time = time.perf_counter()

        # Delegate directly to the production RAGService
        try:
            response = RAGService.answer(
                question=question,
                context_topic=context_topic,
            )
            answer = response.get("answer", "")
            topic = response.get("topic")
            graph_context = response.get("graph_context", [])
            incoming = response.get("incoming", [])
            learning_path = response.get("learning_path", [])
            retrieval_hit = bool(response.get("status") and topic)
        except Exception as e:
            answer = f"Error in KG-RAG execution: {e}"
            topic = None
            graph_context = []
            incoming = []
            learning_path = []
            retrieval_hit = False

        latency_sec = time.perf_counter() - start_time

        return {
            "system": self.SYSTEM_NAME,
            "answer": answer,
            "retrieved_context": {
                "topic": topic,
                "graph_context": graph_context,
                "incoming": incoming,
                "learning_path": learning_path,
            },
            "retrieval_hit": retrieval_hit,
            "latency_sec": round(latency_sec, 3),
        }
