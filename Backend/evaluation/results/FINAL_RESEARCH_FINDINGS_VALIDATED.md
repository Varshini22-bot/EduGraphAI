# Final Research Findings: EduGraphAI Evaluation Study (Validated)

### Finding 1 — Correctness and Generator Fluency
In the double-blind human audit ($N=30$), the unaugmented LLM-only baseline achieved a statistically significantly higher mean Correctness score than EduGraphAI KG-RAG (2.600 vs. 2.133; paired mean difference $-0.467$, Wilcoxon $W = 17.0$, raw $p = 0.00175$, Holm-adjusted $p = 0.00875$, $d_z = -0.685$). When operating with small local language models (`llama3.2`), unconstrained generation produces longer, more elaborative prose that scored higher in subjective human correctness, whereas graph-augmented synthesis produced more concise responses and executed strict refusals on ambiguous topics.

### Finding 2 — Educational Relevance
Both systems demonstrated comparable educational relevance on computer science curriculum questions (2.167 for KG-RAG vs. 2.367 for LLM-Only; paired mean difference $-0.200$, Wilcoxon $W = 9.0$, raw $p = 0.08326$, Holm-adjusted $p = 0.24978$). No statistically significant difference was detected at $$\alpha = 0.05$$.

### Finding 3 — Factual Grounding Under Multiplicity Correction
While unadjusted scoring indicated a nominal difference in factual grounding (raw $p = 0.01963$), **the difference is not statistically significant following Holm-Bonferroni correction** (Holm-adjusted $p = 0.07852 > 0.05$; 95% bootstrap CI [-0.400, -0.067]). Both systems maintained substantial factual grounding across core syllabus concepts.

### Finding 4 — Supported Syllabus Gold-Fact Coverage
On supported syllabus questions ($n=24$), both systems achieved near-ceiling semantic coverage of reference gold facts:
- KG-RAG covered 56 of 60 reference facts (93.3% aggregate; mean question rate 0.931).
- LLM-only covered 60 of 60 reference facts (100.0% aggregate; mean question rate 1.000).
- The paired difference was not statistically significant (Wilcoxon $W = 0.0$, raw $p = 0.10247$, Holm-adjusted $p = 0.24978$).

### Finding 5 — Out-of-Scope Curriculum Handling (Exploratory)
On out-of-scope curriculum questions ($n=6$), KG-RAG exhibited a higher descriptive mean rating in refusing unsupported queries (2.167 vs. 1.333; mean difference $+0.833$, Cohen's $d_z = +0.848$, 95% bootstrap CI [+0.167, +1.500]). However, due to small sample size and $N_r = 3$ non-zero pairs, the Wilcoxon test yielded $p = 0.25000$. This observation is classified as an exploratory descriptive finding indicating directional guardrail capability rather than a confirmed inferential effect.

### Finding 6 — Retrieval Latency Trade-Off
Across the full 120-question benchmark, graph-augmented retrieval incurred an average latency of 47.29 s compared to 20.19 s for the unaugmented baseline (paired mean difference +27.10 s; $2.34x$ latency multiplier). This reflects the computational overhead of entity extraction, Cypher query resolution, and graph context injection.
