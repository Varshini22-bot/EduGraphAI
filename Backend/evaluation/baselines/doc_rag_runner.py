"""
Backend/evaluation/baselines/doc_rag_runner.py

Traditional Document-RAG Baseline Runner for EduGraphAI Research Evaluation.

Implements a conventional unstructured text-retrieval RAG baseline:
- No Neo4j connection.
- No Knowledge Graph traversal or relational topology.
- Retrieves top-k (k=3) relevant text passages from a text corpus using
  deterministic lexical/TF-IDF similarity.
- Injects retrieved text passages into an academic RAG prompt.
"""

import collections
import glob
import math
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Ensure Backend directory is in sys.path
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from llm.answer_generator import generate_answer
from config import LLM_MODEL, LLM_PROVIDER


def _tokenize(text: str) -> List[str]:
    """Simple lowercase word tokenizer."""
    return re.findall(r"\b[a-zA-Z0-9_]+\b", text.lower())


class DocumentIndex:
    """
    Lightweight, deterministic in-memory TF-IDF index for unstructured text chunks.
    Requires only the Python standard library.
    """

    def __init__(self, chunks: List[str]):
        self.chunks = chunks
        self.doc_count = len(chunks)
        self.doc_tokens = [_tokenize(c) for c in chunks]
        self.doc_freqs = [collections.Counter(toks) for toks in self.doc_tokens]
        self.doc_lens = [len(toks) for toks in self.doc_tokens]

        # Calculate document frequencies (DF) for IDF calculation
        self.df = collections.Counter()
        for freqs in self.doc_freqs:
            for term in freqs:
                self.df[term] += 1

        # Smooth Inverse Document Frequency (IDF)
        self.idf = {
            term: math.log((self.doc_count + 1) / (count + 1)) + 1.0
            for term, count in self.df.items()
        }

    def search(self, query: str, top_k: int = 3) -> List[Tuple[float, str]]:
        """
        Retrieves top_k text chunks ranked by cosine similarity over TF-IDF vectors.
        """
        if self.doc_count == 0:
            return []

        q_tokens = _tokenize(query)
        if not q_tokens:
            return [(0.0, c) for c in self.chunks[:top_k]]

        q_freqs = collections.Counter(q_tokens)
        q_vec = {
            t: (cnt / len(q_tokens)) * self.idf.get(t, 1.0)
            for t, cnt in q_freqs.items()
        }
        q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0

        scores = []
        for i, doc_freq in enumerate(self.doc_freqs):
            doc_len = self.doc_lens[i] or 1
            dot = 0.0
            doc_norm_sq = 0.0

            for term, count in doc_freq.items():
                tfidf = (count / doc_len) * self.idf.get(term, 1.0)
                doc_norm_sq += tfidf * tfidf
                if term in q_vec:
                    dot += q_vec[term] * tfidf

            doc_norm = math.sqrt(doc_norm_sq) or 1.0
            score = dot / (q_norm * doc_norm)
            scores.append((score, self.chunks[i]))

        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k]


class DocRAGRunner:
    """
    Traditional Document-RAG baseline runner.
    Indexes plain text documents from a specified corpus directory and answers
    questions using top-3 retrieved text passages.
    """

    SYSTEM_NAME = "doc_rag"

    def __init__(
        self,
        corpus_dir: Optional[str] = None,
        top_k: int = 3,
        model_name: Optional[str] = None,
    ):
        self.top_k = top_k
        self.model_name = model_name or LLM_MODEL
        self.provider = LLM_PROVIDER

        # Default corpus location
        default_dir = os.path.join(_BACKEND_DIR, "evaluation", "corpus")
        self.corpus_dir = corpus_dir or default_dir
        self.index = self._load_corpus()

    def _load_corpus(self) -> DocumentIndex:
        """
        Loads and chunks text files (.txt, .md) from the corpus directory.
        If corpus directory is empty, creates an empty DocumentIndex.
        """
        chunks: List[str] = []
        if os.path.isdir(self.corpus_dir):
            files = sorted(
                glob.glob(os.path.join(self.corpus_dir, "**", "*.txt"), recursive=True)
                + glob.glob(os.path.join(self.corpus_dir, "**", "*.md"), recursive=True)
            )
            for filepath in files:
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    # Chunk by paragraphs (double newlines) or size limits
                    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 40]
                    chunks.extend(paragraphs)
                except Exception as e:
                    print(f"[DOC-RAG] Warning reading corpus file '{filepath}': {e}")

        return DocumentIndex(chunks)

    def _build_prompt(
        self, question: str, retrieved_docs: List[str], marks: Optional[int] = None
    ) -> str:
        """Builds standard document-augmented RAG prompt without graph topology."""
        marks_instruction = (
            f" Structure the answer appropriately for a {marks}-mark university exam question."
            if marks
            else ""
        )

        docs_text = "\n\n".join(
            f"[Document {i+1}]\n{doc}" for i, doc in enumerate(retrieved_docs)
        )

        return (
            "You are an academic educational assistant.\n"
            "Answer the student's question using ONLY the provided reference documents as factual grounding.\n"
            "If the reference documents do not contain sufficient information to answer the question, "
            "clearly state that the topic is not covered in the reference material.\n"
            f"{marks_instruction}\n\n"
            "==================================================\n"
            "REFERENCE DOCUMENTS\n"
            "==================================================\n"
            f"{docs_text if docs_text else 'No reference documents available in the corpus.'}\n\n"
            "==================================================\n"
            "QUESTION\n"
            "==================================================\n"
            f"{question.strip()}\n\n"
            "Answer:"
        )

    def run(self, question: str, marks: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Executes traditional Document-RAG for a given question.

        Args:
            question: Natural language question.
            marks: Optional mark weight (2, 5, 8, 10).

        Returns:
            Dict containing system identifier, answer text, retrieved_context,
            retrieval_hit, and latency in seconds.
        """
        start_time = time.perf_counter()

        # 1. Retrieve top-k text chunks
        results = self.index.search(question, top_k=self.top_k)
        retrieved_chunks = [chunk for score, chunk in results]
        retrieval_hit = len(retrieved_chunks) > 0 and results[0][0] > 0.05

        # 2. Build Document-RAG prompt
        prompt = self._build_prompt(question, retrieved_chunks, marks=marks)
        num_predict = kwargs.get("num_predict")

        # 3. Generate answer
        try:
            if not retrieved_chunks:
                answer = (
                    "No reference documents are currently available in the document corpus "
                    f"to answer the question: '{question}'."
                )
            else:
                answer = generate_answer(prompt, num_predict=num_predict)
        except Exception as e:
            answer = f"Error generating answer: {e}"

        latency_sec = time.perf_counter() - start_time

        return {
            "system": self.SYSTEM_NAME,
            "answer": answer,
            "retrieved_context": retrieved_chunks,
            "retrieval_hit": retrieval_hit,
            "latency_sec": round(latency_sec, 3),
        }
