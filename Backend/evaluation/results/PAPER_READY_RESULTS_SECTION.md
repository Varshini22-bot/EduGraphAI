# Results Section (Manuscript-Ready Draft)

## Experimental Evaluation

We evaluated EduGraphAI against an LLM-only baseline across 120 standardized computer science examination questions spanning six domains (ADA, CN, DSA, ML, OS, and SEPM). To assess generation quality, a stratified 30-question subset (24 supported curriculum questions and 6 out-of-scope questions) was evaluated by a human domain researcher under double-blind conditions using a validated 0–3 rubric across Correctness, Educational Relevance, Factual Grounding, Gold-Fact Coverage, and Unsupported Topic Handling.

### Generation Quality & Curriculum Boundary Enforcement
As presented in Table 1, on out-of-scope questions, EduGraphAI KG-RAG demonstrated a notable advantage in curriculum boundary enforcement compared to the LLM-only baseline (mean 2.167 vs. 1.333; paired mean difference $d = +0.833$, Cohen's $d_z = +0.85$, 95% bootstrap CI [+0.167, +1.500]). While the baseline consistently provided ungrounded technical explanations for out-of-scope concepts, KG-RAG successfully recognized curriculum boundaries and provided syllabus redirection.

On supported curriculum questions, both systems achieved high semantic gold-fact coverage (93.3% for KG-RAG vs. 100.0% for LLM-only; Wilcoxon signed-rank $W = 0.0$, $p = 0.25$). The baseline achieved higher correctness scores on supported queries (2.6 vs. 2.133; $d = -0.467$, $p = 0.0021$), reflecting the greater fluency and expansive elaboration of unconstrained generation on small local models. Educational relevance remained comparable across both approaches (2.167 vs. 2.367; $p = 0.15$).

### Latency Overhead
Across the full 120-question benchmark, KG-RAG exhibited an average response latency of 47.29 s ($SD = 15.65$ s) compared to 20.19 s ($SD = 7.15$ s) for the LLM-only baseline, representing a paired mean difference of +27.10 s (a 2.34× factor). This latency reflects the additional computation required for entity extraction, Cypher query execution, and multi-hop graph context serialization prior to generation.

### Evaluator Calibration
Comparison between the human audit and an automated LLM judge (`phi4-mini:latest`) revealed exact score agreement rates of 55.0% for Correctness, 38.3% for Relevance, and 43.3% for Grounding. The automated evaluator exhibited systematic leniency bias (+0.38 to +0.65 points), reinforcing the necessity of human ground-truth validation for pedagogical benchmark assessment.
