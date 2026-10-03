# Publication-Ready Tables: EduGraphAI Evaluation Study

This document compiles the complete set of publication-ready tables presenting empirical findings from the EduGraphAI research evaluation.

---

### Table 1: Benchmark Composition and Taxonomy
The standardized evaluation dataset comprises 120 questions distributed uniformly across six computer science disciplines and five pedagogical query categories.

| Subject | Domain Focus | Factual (2m) | Conceptual (5m) | Comparison (5m/10m) | Relationship (5m/10m) | Unsupported / Out-of-Scope (0m) | Total Questions | Supported Queries | Unsupported Queries |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADA** | Analysis & Design of Algorithms | 4 | 4 | 4 | 4 | 4 | 20 | 16 | 4 |
| **CN** | Computer Networks | 4 | 4 | 4 | 4 | 4 | 20 | 16 | 4 |
| **DSA** | Data Structures & Algorithms | 4 | 4 | 4 | 4 | 4 | 20 | 16 | 4 |
| **ML** | Machine Learning | 4 | 4 | 4 | 4 | 4 | 20 | 16 | 4 |
| **OS** | Operating Systems | 4 | 4 | 4 | 4 | 4 | 20 | 16 | 4 |
| **SEPM** | Software Engineering & Project Mgmt | 4 | 4 | 4 | 4 | 4 | 20 | 16 | 4 |
| **Total** | **All 6 Disciplines** | **24** | **24** | **24** | **24** | **24** | **120** | **96** | **24** |

*Notes:*
- Supported questions ($n=96$) target syllabus concepts with defined canonical nodes in the Neo4j knowledge graph.
- Unsupported questions ($n=24$) assess system guardrails on out-of-scope technical topics outside the defined syllabus.
- Marks indicate target examination weight (2 marks = brief definition; 5 marks = conceptual exposition; 10 marks = comprehensive comparative/relationship analysis).

---

### Table 2: Validated Human Evaluation Results with Holm-Bonferroni Multiplicity Correction
Stratified double-blind evaluation conducted by a domain researcher on $N=30$ paired items. Differences are calculated as $\text{KG-RAG} - \text{LLM-Only}$ (negative values favor the baseline; positive values favor KG-RAG). Hypothesis tests are two-sided Wilcoxon signed-rank tests with zero-difference pruning (`zero_method='wilcox'`). Multiplicity adjustment is conducted via the Holm-Bonferroni step-down procedure ($\alpha = 0.05$). Confidence intervals are 95% percentile bootstrap intervals ($B=10,000$, seed 42).

| Metric | Sample ($n$) | KG-RAG Mean | LLM-Only Mean | Mean Diff ($d$) | Median Diff | 95% Bootstrap CI | Wilcoxon $W$ | Raw $p$-value | Holm Adjusted $p$ | Effect Size ($d_z$) | Validated Statistical Conclusion ($\alpha = 0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Correctness** | 30 | 2.133 | 2.600 | $-0.467$ | $-0.500$ | $[-0.700, -0.233]$ | 17.0 | $0.00175$ | **$0.00875$** | $-0.685$ | **Statistically Significant** ($p < 0.01$, favors Baseline) |
| **Educational Relevance** | 30 | 2.167 | 2.367 | $-0.200$ | $0.000$ | $[-0.433, +0.000]$ | 9.0 | $0.08326$ | $0.24978$ | $-0.328$ | Not Significant ($p = 0.25$) |
| **Factual Grounding** | 30 | 2.167 | 2.400 | $-0.233$ | $0.000$ | $[-0.400, -0.067]$ | 5.0 | $0.01963$ | $0.07852$ | $-0.463$ | **Not Significant After Holm Correction** ($p > 0.05$) |
| **Gold-Fact Coverage Rate** | 24 | 0.931 | 1.000 | $-0.069$ | $0.000$ | $[-0.153, +0.000]$ | 0.0 | $0.10247$ | $0.24978$ | $-0.366$ | Not Significant ($p = 0.25$) |
| **Unsupported Handling** | 6 | 2.167 | 1.333 | $+0.833$ | $+0.500$ | $[+0.167, +1.500]$ | 0.0 | $0.25000$ | $0.25000$ | $+0.848$ | **Exploratory Finding** (Not Significant, $p = 0.25$) |

*Notes:*
- Gold-Fact Coverage Rate evaluated on $n=24$ supported queries (encompassing 60 reference facts). Aggregate coverage: KG-RAG 56/60 (93.3%); LLM-Only 60/60 (100.0%).
- Unsupported Handling evaluated on $n=6$ out-of-scope curriculum queries. Non-zero paired differences $N_r = 3$.
- In the primary 3-metric family, Factual Grounding yields $p = 0.03926$. Across the full 5-outcome evaluation family, Factual Grounding yields $p = 0.07852$, failing to achieve significance at $\alpha = 0.05$.

---

### Table 3: Response Latency Comparison on Full Benchmark
Measurement of end-to-end response generation latency across the entire 120-question evaluation corpus.

| System Architecture | Benchmark Sample ($N$) | Mean Latency (seconds) | Standard Deviation ($SD$) | Median Latency (seconds) | Interquartile Range (IQR) | Latency Overhead vs Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LLM-Only Baseline** | 120 | 20.190 s | 7.152 s | 19.340 s | 8.420 s | Baseline ($1.00\times$) |
| **EduGraphAI KG-RAG** | 120 | 47.294 s | 15.654 s | 44.180 s | 18.910 s | **+27.104 s ($2.34\times$)** |

*Notes:*
- Latency experiment executed using local Ollama daemon (`llama3.2:latest`, context window 4096 tokens) on identical hardware.
- Graph retrieval pipeline latency includes entity extraction, Cypher query execution, multi-hop relationship resolution, and formatted context injection.
- Response latency measurements are completely independent of the $N=30$ human quality audit sample.

---

### Table 4: Subject-Level Descriptive Breakdown
Descriptive quality metrics and reference fact counts across academic disciplines ($n=5$ questions per subject in human audit).

| Subject Discipline | Sample ($n$) | KG-RAG Correctness | LLM-Only Correctness | KG-RAG Relevance | LLM-Only Relevance | KG-RAG Grounding | LLM-Only Grounding | KG-RAG Gold Facts | LLM-Only Gold Facts | Total Reference Facts |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADA** | 5 | 2.20 | 2.80 | 2.20 | 2.20 | 2.40 | 3.00 | 10 | 10 | 10 |
| **CN** | 5 | 2.40 | 3.00 | 2.40 | 3.00 | 2.20 | 2.60 | 9 | 10 | 10 |
| **DSA** | 5 | 2.40 | 2.60 | 2.60 | 2.80 | 2.40 | 2.40 | 7 | 10 | 10 |
| **ML** | 5 | 2.60 | 2.60 | 2.40 | 2.40 | 2.60 | 2.80 | 10 | 10 | 10 |
| **OS** | 5 | 1.60 | 2.60 | 1.60 | 2.00 | 1.80 | 2.00 | 10 | 10 | 10 |
| **SEPM** | 5 | 1.60 | 2.00 | 1.80 | 1.80 | 1.60 | 1.60 | 10 | 10 | 10 |

*Notes:*
- Due to small sample size per subject ($n=5$), these metrics are strictly descriptive and intended for exploratory diagnostic inspection.
- Gold facts evaluated on the 4 supported questions per subject (10 total facts per subject across 4 questions).

---

### Table 5: Category-Level Descriptive Breakdown
Descriptive quality metrics across pedagogical query categories ($n=6$ questions per category in human audit).

| Question Category | Sample ($n$) | KG-RAG Correctness | LLM-Only Correctness | Mean Diff Correctness | KG-RAG Relevance | LLM-Only Relevance | Mean Diff Relevance | KG-RAG Grounding | LLM-Only Grounding | Mean Diff Grounding |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Factual** | 6 | 2.667 | 2.667 | $+0.000$ | 2.333 | 2.333 | $+0.000$ | 2.667 | 2.667 | $+0.000$ |
| **Conceptual** | 6 | 2.500 | 2.667 | $-0.167$ | 2.833 | 2.667 | $+0.167$ | 2.500 | 2.667 | $-0.167$ |
| **Comparison** | 6 | 2.333 | 3.000 | $-0.667$ | 2.000 | 2.333 | $-0.333$ | 2.167 | 2.500 | $-0.333$ |
| **Relationship** | 6 | 1.667 | 2.500 | $-0.833$ | 2.000 | 2.333 | $-0.333$ | 1.833 | 2.167 | $-0.333$ |
| **Unsupported** | 6 | 1.500 | 2.167 | $-0.667$ | 1.667 | 2.167 | $-0.500$ | 1.667 | 2.000 | $-0.333$ |

*Notes:*
- Factual and conceptual questions exhibited close parity between systems.
- Differences favoring the baseline appeared predominantly on complex comparison and relationship queries where open-ended elaboration received higher subjective marks.
- On unsupported queries, human scoring reflects answering the question vs. refusing; pedagogical handling is captured in Table 2's Unsupported Handling metric (+0.833 mean difference favoring KG-RAG).
