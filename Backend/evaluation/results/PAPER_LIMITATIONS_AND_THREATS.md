# Evaluation Limitations and Threats to Validity: EduGraphAI

This document provides a comprehensive analysis of the methodological constraints, scope limitations, and threats to validity associated with the EduGraphAI empirical evaluation study.

---

## 1. Core Architectural Limitations

### 1.1 Language Model Discrepancy (Evaluation vs. Production Runtime)
- **Observed Configuration**: The experimental benchmark and human evaluation audit were conducted using a locally hosted 3-billion-parameter language model (`llama3.2:latest`) executed via the Ollama runtime on consumer hardware (`OLLAMA_NUM_CTX=4096`).
- **Production Configuration**: The live deployed EduGraphAI production system utilizes the Groq Cloud API hosting `llama-3.3-70b-versatile` (a 70-billion-parameter dense model).
- **Impact on Findings**: Small local models (3B) exhibit distinct behavioral trade-offs compared to large frontier models (70B). Specifically, smaller models have lower context-processing bandwidth and can produce constrained or truncated responses when provided with complex multi-hop graph contexts, whereas their unconstrained generation may rely on memorized pretraining surface patterns that read as more fluent or verbose. Consequently, the findings reported in this evaluation represent the behavior of the system under localized, resource-constrained execution and do not constitute a direct performance measurement of the production cloud architecture.

### 1.2 Document-RAG Corpus Availability
- **Limitation**: The current evaluation compares Knowledge Graph-grounded generation (KG-RAG) against an unaugmented language model (LLM-only baseline). An ideal three-way comparison would additionally benchmark traditional Document-based Retrieval-Augmented Generation (Document-RAG / vector search over textbook PDFs).
- **Rationale**: A standardized, high-quality, unstructured textbook corpus spanning all six academic subjects was not uniformly available in the repository. Evaluating Document-RAG on an incomplete or synthetic document set would have introduced uncontrolled confounding variables.
- **Scope Boundary**: The empirical conclusions of this study are strictly restricted to the comparison between KG-RAG and LLM-only generation. No claims are made regarding the relative merits of Knowledge Graphs versus dense vector passage retrieval.

---

## 2. Threats to Validity

### 2.1 Internal Validity
- **Entity Extraction Precision**: In the KG-RAG pipeline, retrieval quality depends directly on the `TopicExtractor` component accurately mapping question text to canonical graph nodes. Ambiguities in query phrasing or partial entity matches can lead to the retrieval of tangential subgraphs, injecting noisy or incomplete context into the prompt.
- **Evaluator Subjectivity**: Generation quality was assessed by a human domain researcher. Although the evaluation followed a pre-registered rubric and double-blind presentation (randomizing Answer A and Answer B to prevent confirmation bias), individual human evaluators may exhibit subtle preferences for stylistic elaboration over conciseness.
- **Benchmark Item Distribution**: Questions were constructed to reflect typical university examination queries across standardized mark weights (2, 5, 10 marks). While representative of curriculum assessments, question formulation may inadvertently favor certain structural styles.

### 2.2 External Validity
- **Academic Domain Breadth**: The benchmark evaluates six computer science disciplines (ADA, CN, DSA, ML, OS, and SEPM). While these disciplines cover theoretical, mathematical, and systems-level topics, findings may not generalize directly to humanities, clinical medicine, or legal education where concept ontologies have different topological characteristics.
- **Sample Scale**: The benchmark contains 120 questions, and the double-blind human audit evaluated 30 stratified items. Subgroup analyses at the subject level ($n=5$ per subject) and unsupported-topic level ($n=6$) are inherently restricted in generalizability.
- **Target Audience Calibration**: The system was evaluated using undergraduate computer science curriculum concepts. Educational assistants tailored for primary education or postgraduate research may exhibit different interaction dynamics.

### 2.3 Construct Validity
- **Measurement of Correctness and Grounding**: Human scoring utilized an ordinal 0–3 rubric. While rubric anchors were explicitly defined, capturing "factual grounding" independently of "correctness" is challenging because factual inaccuracies inevitably depress perceived correctness.
- **Reference Gold-Fact Construction**: Gold-fact coverage was assessed against 60 reference facts created alongside the benchmark. Variations in reference fact granularity can affect whether a fact is judged as semantically covered by an answer.
- **Curriculum Guardrail Scoring**: On unsupported queries, human scorers rated Answer A and Answer B on whether the system answered or refused. The distinction between a helpful refusal and an incomplete response depends heavily on pedagogical philosophy.

### 2.4 Statistical Validity
- **Non-Parametric Assumptions**: The evaluation correctly adopted paired, two-sided Wilcoxon signed-rank tests rather than parametric $t$-tests to handle ordinal, non-normal rating data.
- **Multiple-Comparison Corrections**: Testing five outcome metrics without correction would elevate family-wise Type I error to approximately $1 - (1 - 0.05)^5 \approx 22.6\%$. Applying the Holm-Bonferroni step-down procedure controlled the family-wise error rate at $\alpha = 0.05$, which directly altered the interpretation of Factual Grounding from nominally significant ($p = 0.0196$) to non-significant ($p = 0.0785$).
- **Statistical Power in Subsets**: For unsupported-topic handling ($n=6$), only $N_r = 3$ non-zero paired differences were observed. In a discrete permutation test, the minimum possible two-sided $p$-value for $N_r = 3$ is $2 / 2^3 = 0.2500$. Therefore, this test was mathematically incapable of achieving statistical significance at $\alpha = 0.05$, necessitating its formal classification as an exploratory finding despite a large sample effect size ($d_z = +0.848$) and a positive bootstrap confidence interval.
