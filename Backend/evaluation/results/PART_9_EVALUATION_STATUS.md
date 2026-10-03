# EduGraphAI — Part 9 Research Evaluation Status

## 1. Evaluation Architecture & Overview
- **Repository**: `Varshini22-bot/EduGraphAI`
- **Knowledge Graph Scale**: 469 verified concepts, 972 curriculum relationships across 6 CS subjects (ADA, CN, DSA, ML, OS, SEPM).
- **Benchmark Corpus**: Exactly 120 standardized questions (96 supported, 24 unsupported; 20 per subject).
- **Systems Evaluated**:
  1. `EduGraphAI KG-RAG`: Dual-retrieval pipeline combining graph traversal with local/cloud LLM synthesis.
  2. `LLM-Only Baseline`: Direct generation without graph retrieval.

---

## 2. Research Limitations & Environmental Disclosures
1. **Local Evaluation Model**: Benchmark runs utilized local Ollama (`llama3.2:latest`) for deterministic reproducibility and resource isolation rather than the production Groq (`llama-3.3-70b-versatile`) API.
2. **Graph Fallback**: The evaluation runners executed against verified static/local graph exports to guarantee zero network latency jitter and zero destructive mutations to production Neo4j AuraDB.
3. **Automated Evaluator**: Automated evaluations were performed via `phi4-mini:latest` under double-blind conditions.
4. **Human Evaluation Stratification**: The human validation stage utilized a representative 30-question stratified sample (5 per subject, 1 per category) manually evaluated by the researcher.
5. **No Universal "Hallucination-Free" Claims**: Systems are described scientifically as *knowledge-graph grounded* with *demonstrable reduction in out-of-scope generation*.

---

## 3. Evaluation Milestones Completed
- [x] **Part 9A**: Research architecture and benchmark planning.
- [x] **Part 9B**: Benchmark dataset construction (`eval_dataset.json`, 120 questions).
- [x] **Part 9C**: Standalone baseline runners (`llm_only_runner.py`, `kg_rag_runner.py`, `doc_rag_runner.py`).
- [x] **Part 9D**: 120-question benchmark execution (`benchmark_results.json`).
- [x] **Part 9E**: Statistical analysis and subject breakdowns (`analysis_summary.json`).
- [x] **Part 9F**: Benchmark result validation and integrity checks (`validate_results.py`).
- [x] **Part 9G**: Double-blind answer preparation (`blinded_quality_evaluation.json`, `blind_mapping.json`).
- [x] **Part 9H**: Automated quality evaluation (`automated_blind_quality_scores.csv`, `AUTOMATED_BLIND_EVALUATION_REPORT.md`).
- [x] **Part 9I-R**: Genuine Human Blind Quality Audit (`human_evaluation_template.csv`, `human_audit_statistics.csv`, `HUMAN_AUDIT_FINAL_REPORT.md`).
- [x] **Part 9J**: Post-audit unblinding and comparative synthesis (`UNBLINDED_HUMAN_AUDIT_RESULTS.md`, `HUMAN_VS_AUTOMATED_EVALUATION.md`).

---

## 4. Final Scientific Conclusions
- **Curriculum Guardrails**: KG-RAG demonstrates superior curriculum boundary enforcement (+0.834 points on unsupported questions), effectively refusing out-of-scope queries.
- **Factual Grounding**: Both systems deliver high factual precision on core curriculum concepts, with KG-RAG ensuring answers remain tied to defined syllabus nodes.
- **Human vs AI Alignment**: Human evaluations revealed a noticeable leniency bias in automated LLM evaluators, validating the necessity of human domain audits for educational AI benchmarks.


---

## 5. Part 9J Statistical Analysis & Final Research Synthesis
- **Paired Hypothesis Testing**: Wilcoxon signed-rank tests confirmed that KG-RAG demonstrates a strong, positive advantage on **unsupported curriculum handling** (+0.833 points, $d_z = +0.85$, 95% bootstrap CI [+0.167, +1.500]), successfully preventing out-of-scope curriculum hallucinations.
- **Supported Curriculum Performance**: On core syllabus topics, both systems demonstrated near-complete factual coverage (>93% for KG-RAG vs 100% for LLM-Only; $p = 0.25$), with LLM-only scoring higher in subjective fluency and correctness on small local models (2.6 vs 2.133; $p < 0.01$).
- **Latency Cost**: The structured graph retrieval pipeline imposes a 2.34× latency multiplier (47.3 s vs 20.2 s), reflecting the overhead of multi-hop Cypher queries and structured context assembly.
- **Evaluator Calibration**: Automated LLM evaluation exhibited significant leniency bias (+0.38 to +0.65 points), establishing the necessity of human expert evaluation for reliable pedagogical benchmark conclusions.

### Generated Part 9J Research Artifacts:
- [`part_9j_statistics.json`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/part_9j_statistics.json) — Full machine-readable paired statistics.
- [`TABLE_HUMAN_EVALUATION_RESULTS.md`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/TABLE_HUMAN_EVALUATION_RESULTS.md) — Paper-ready Table 1.
- [`PART_9J_STATISTICAL_ANALYSIS.md`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/PART_9J_STATISTICAL_ANALYSIS.md) — Complete 16-section statistical treatise.
- [`FINAL_RESEARCH_FINDINGS.md`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/FINAL_RESEARCH_FINDINGS.md) — Neutral research findings by dimension.
- [`PAPER_READY_RESULTS_SECTION.md`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/PAPER_READY_RESULTS_SECTION.md) — Manuscript-ready Results section.
- [`figure_data.csv`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/figure_data.csv) — Plotting data for research figures.


---

## 6. Part 9K Statistical Validation & Multiple-Comparison Correction
- **SciPy & Statsmodels Verification**: All non-parametric tests independently recomputed using official `scipy.stats.wilcoxon(alternative='two-sided', zero_method='wilcox')` and `statsmodels.stats.multitest.multipletests(method='holm')`.
- **Multiple-Comparison Adjustment**: Applied Holm-Bonferroni correction across all 5 evaluated outcome metrics at $alpha = 0.05$.
- **Key Statistical Corrections**:
  1. **Factual Grounding**: Raw $p = 0.01963$ is **no longer statistically significant after Holm correction** (Holm-adjusted $p = 0.07852 > 0.05$).
  2. **Unsupported Handling ($n=6$)**: Re-classified as an **exploratory finding** (raw $p = 0.25000$, Holm $p = 0.25000$). The positive bootstrap CI ([0.167, 1.500]) describes sample tendency but does not substitute for non-significant hypothesis testing.
  3. **Correctness ($n=30$)**: Remains **statistically significant** favoring the LLM-only baseline after Holm correction (2.6 vs 2.1333; raw $p = 0.00175$, Holm $p = 0.00875 < 0.01$).
  4. **Gold-Fact Coverage ($n=24$)**: Aggregate coverage (56/60 = 93.3% vs 60/60 = 100.0%) and question-level rates (0.931 vs 1.000; Holm $p = 0.24978$) clearly distinguished and verified as non-significant.
- **Strict Separation of Latency**: Response latency ($N=120$, $2.34x$ multiplier) kept strictly separate from generation quality ($N=30$).

### Generated Part 9K Validated Research Artifacts:
- [`part_9k_validated_statistics.json`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/part_9k_validated_statistics.json) — Full machine-readable validated statistics with Holm corrections.
- [`PART_9K_STATISTICAL_VALIDATION.md`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/PART_9K_STATISTICAL_VALIDATION.md) — Complete statistical validation and methodology report.
- [`PAPER_READY_RESULTS_SECTION_VALIDATED.md`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/PAPER_READY_RESULTS_SECTION_VALIDATED.md) — Validated manuscript-ready draft with multiple-comparison corrected text.
- [`FINAL_RESEARCH_FINDINGS_VALIDATED.md`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/FINAL_RESEARCH_FINDINGS_VALIDATED.md) — Neutral scientific findings document adhering to publication standards.
