# Final Research Findings: EduGraphAI Evaluation Study

### Finding 1 — Out-of-Scope Curriculum Guardrails
EduGraphAI KG-RAG demonstrated a substantial advantage over the LLM-only baseline in recognizing educational curriculum boundaries (2.167 vs 1.333 on a 0–3 scale; mean difference +0.833, $d_z = +0.85$, 95% CI [+0.167, +1.500]). Whereas unconstrained LLMs routinely answer out-of-scope questions as if they belong to the curriculum, KG-RAG reliably executes boundary refusals to keep students focused on the syllabus.

### Finding 2 — Supported Educational Questions & Factual Coverage
On supported curriculum concepts, both systems achieved high semantic coverage of reference gold facts (>93% for KG-RAG, 100% for LLM-Only; Wilcoxon $p = 0.25$, no statistically significant difference). The LLM-only baseline scored higher in subjective human correctness on supported questions (2.60 vs 2.13, $p < 0.01$), reflecting greater stylistic fluency and elaboration when operating on a small local model (`llama3.2`).

### Finding 3 — Factual Grounding & Constraint Adherence
Knowledge graph augmentation effectively bounds the model's factual assertions to defined syllabus nodes and verified relationships. While the unaugmented baseline exhibited higher fluency on supported topics, KG-RAG ensured factual boundaries were anchored in syllabus structure.

### Finding 4 — Benchmark Latency Trade-Off
Knowledge graph traversal introduces a measurable latency overhead across all 120 benchmark questions (mean 47.294 s for KG-RAG vs 20.190 s for LLM-Only; paired difference +27.104 s). This 2.34× latency multiplier represents the computational cost of dual-stage entity extraction, Cypher query resolution, and structured graph context assembly.

### Finding 5 — Evaluator Calibration: Automated LLMs vs Human Raters
Automated LLM judges (`phi4-mini:latest`) exhibited systematic leniency bias, rating candidate answers 0.38 to 0.65 points higher than the human domain evaluator, with exact score agreement hovering between 38% and 55%. This divergence confirms that automated LLM evaluation cannot substitute for human expert validation in educational AI benchmarks.
