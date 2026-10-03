"""
Backend/evaluation/baselines/llm_only_runner.py

Ungrounded LLM Baseline Runner for EduGraphAI Research Evaluation.

Generates answers to educational questions purely using the parametric memory
of the configured LLM (e.g. Groq llama-3.3-70b-versatile or local Ollama),
without Knowledge Graph retrieval or document augmentation.
"""

import os
import sys
import time
from typing import Any, Dict, Optional

# Ensure Backend directory is in sys.path
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from llm.answer_generator import generate_answer
from config import LLM_PROVIDER, LLM_MODEL


class LLMOnlyRunner:
    """
    Ungrounded LLM baseline runner.
    Sends questions directly to the configured LLM with an educational prompt
    and zero retrieval context.
    """

    SYSTEM_NAME = "llm_only"

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or LLM_MODEL
        self.provider = LLM_PROVIDER

    def _build_prompt(self, question: str, marks: Optional[int] = None) -> str:
        """Constructs an ungrounded, general academic prompt."""
        marks_instruction = (
            f" Please tailor the depth and detail of your explanation for a {marks}-mark university examination question."
            if marks
            else ""
        )
        return (
            "You are an academic educational assistant.\n"
            "Answer the following computer science exam question accurately, clearly, and thoroughly "
            f"based on your general knowledge.{marks_instruction}\n\n"
            f"Question:\n{question.strip()}\n\n"
            "Answer:"
        )

    def run(self, question: str, marks: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Executes the ungrounded baseline for a given question.

        Args:
            question: Natural language exam question.
            marks: Optional examination mark weight (2, 5, 8, 10).

        Returns:
            Dict containing system identifier, answer text, and latency in seconds.
        """
        prompt = self._build_prompt(question, marks=marks)
        num_predict = kwargs.get("num_predict")

        start_time = time.perf_counter()
        try:
            answer = generate_answer(prompt, num_predict=num_predict)
        except Exception as e:
            answer = f"Error generating answer: {e}"
        latency_sec = time.perf_counter() - start_time

        return {
            "system": self.SYSTEM_NAME,
            "answer": answer,
            "latency_sec": round(latency_sec, 3),
        }
