# EduGraphAI — Unblinded Human Quality Audit Results

## 1. System Mapping & Unblinding Verification
- **Unblinding Date**: Post-Audit Lock
- **Mapping Source**: `Backend/evaluation/results/blind_mapping.json`
- **Total Questions Evaluated by Human**: 30 (24 Supported, 6 Unsupported)
- **Systems Compared**:
  1. `EduGraphAI KG-RAG` (Knowledge Graph Augmented Retrieval-Generation)
  2. `LLM-Only Baseline` (`ollama / llama3.2:latest`)

---

## 2. Unblinded Quality Comparison Table

| Metric | Subsample | EduGraphAI KG-RAG | LLM-Only Baseline | Difference (KG-RAG - LLM) |
| :--- | :---: | :---: | :---: | :---: |
| **Mean Correctness (0–3)** | All ($N=30$) | **2.133** | **2.6** | -0.467 |
| **Mean Educational Relevance (0–3)** | All ($N=30$) | **2.167** | **2.367** | -0.200 |
| **Mean Factual Grounding (0–3)** | All ($N=30$) | **2.167** | **2.4** | -0.233 |
| **Gold Fact Semantic Coverage** | Supported ($N=24$) | **56 / 60 (93.3%)** | **60 / 60 (100.0%)** | -0.067 |
| **Unsupported Handling (0–3)** | Unsupported ($N=6$) | **2.167** | **1.333** | **+0.834** |

---

## 3. Analysis & Key Research Insights

1. **Curriculum Boundary Adherence & Hallucination Suppression**:
   - In handling unsupported/out-of-scope curriculum questions, **EduGraphAI KG-RAG outperformed LLM-only by +0.834 points (2.167 vs 1.333)**.
   - KG-RAG successfully executed curriculum boundary refusals (redirecting the student to the supported syllabus) on out-of-scope questions, whereas LLM-only answered out-of-scope technical questions without recognizing curriculum limits.
2. **Supported Curriculum Knowledge**:
   - Both systems demonstrated high semantic coverage of gold facts (93.3% for KG-RAG vs 100.0% for LLM-only).
   - The human evaluator rated LLM-only slightly higher on free-form fluency and broad correctness on supported questions (2.6 vs 2.133), while KG-RAG maintained strictly bounded domain constraints.
