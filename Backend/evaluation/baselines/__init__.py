"""
Backend/evaluation/baselines/__init__.py

Package initialization for EduGraphAI research evaluation baseline runners:
- LLMOnlyRunner: Ungrounded parametric baseline using the configured project LLM.
- DocRAGRunner: Traditional unstructured text chunk retrieval RAG baseline.
- KGRAGRunner: EduGraphAI Knowledge-Graph-grounded RAG runner.
"""

from .llm_only_runner import LLMOnlyRunner
from .doc_rag_runner import DocRAGRunner
from .kg_rag_runner import KGRAGRunner

__all__ = ["LLMOnlyRunner", "DocRAGRunner", "KGRAGRunner"]
