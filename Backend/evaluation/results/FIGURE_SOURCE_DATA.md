# EduGraphAI — Publication Figure Source Data & Statistical Grounding

This document provides the authoritative numerical records, confidence intervals, statistical test parameters, and data sources corresponding to all publication-ready figures generated for the EduGraphAI research paper.

All data points in this document are strictly grounded in:
- `Backend/evaluation/results/part_9k_validated_statistics.json`
- `Backend/evaluation/results/benchmark_results.json`
- `Backend/evaluation/results/analysis_summary.json`
- `Backend/evaluation/results/figure_data.csv`
- `Backend/evaluation/results/PAPER_TABLES.md`

All figures carry the mandatory attribution label:
`"Source: EduGraphAI Part 9K validated evaluation"`

---

## 1. Figure Inventory & Specifications

| Figure | Filename | Dimensions | DPI | Visual Design Type | Primary Data Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Figure 1** | `Figure_1_EduGraphAI_Architecture.png` | 4350 × 2280 px | 300 | 5-Stage Sequential Pipeline | System Architecture & Ontologies |
| **Figure 2** | `Figure_2_Evaluation_Pipeline.png` | 3960 × 2280 px | 300 | Dual Comparative Flowchart ($N=120$ vs $N=30$) | Benchmark & Audit Protocol |
| **Figure 3** | `Figure_3_Human_Evaluation_Scores.png` | 3960 × 1620 px | 300 | 3-Panel Grouped Bar Chart with 95% Bootstrap CIs | `part_9k_validated_statistics.json` |
| **Figure 4** | `Figure_4_Local_Benchmark_Latency.png` | 3450 × 1620 px | 300 | 2-Panel Comparison (Mean Bar + Boxplot with Jitter) | `benchmark_results.json` ($N=120$) |

---

## 2. Figure 3: Validated Double-Blind Human Evaluation Data ($N=30$)

### 2.1 Overview & Methodology
- **Design**: Within-subjects paired double-blind audit conducted by human researcher.
- **Sample**: Stratified sample of 30 questions (5 per subject across 6 subjects; 24 syllabus-supported, 6 out-of-scope unsupported).
- **Scale**: Pre-registered ordinal rating scale from 0 to 3 ($0 = \text{Unsatisfactory/Fails}$, $1 = \text{Marginal}$, $2 = \text{Good}$, $3 = \text{Excellent}$).
- **Hypothesis Testing**: Two-sided paired Wilcoxon signed-rank test (`zero_method='wilcox'`).
- **Multiplicity Correction**: Holm-Bonferroni step-down procedure ($\alpha = 0.05$).
- **Confidence Intervals**: 95% Percentile Bootstrap ($B = 10{,}000$ resamples, random seed = 42).
- **Effect Size**: Paired Cohen's $d_z = \frac{\bar{d}}{\text{SD}(d)}$ with $\text{ddof} = 1$.

### 2.2 Primary Evaluation Metrics (Panel A)

| Metric | Sample ($n$) | Non-Zero Pairs ($n_{\neq 0}$) | KG-RAG Mean [95% CI] | LLM-Only Mean [95% CI] | Paired Difference [95% CI] | Median Difference | SD ($d$) | Cohen's $d_z$ | Wilcoxon $W$ | Raw $p$ | Holm $p$ | Statistical Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Correctness** | 30 | 17 | 2.133 [1.833, 2.400] | 2.600 [2.333, 2.800] | -0.467 [-0.700, -0.233] | -0.500 | 0.6814 | -0.6848 | 17.0 | 0.00175 | **0.00875** | **Significant** (Favors LLM-Only) |
| **Educational Relevance** | 30 | 9 | 2.167 [1.900, 2.400] | 2.367 [2.133, 2.567] | -0.200 [-0.433, +0.000] | 0.000 | 0.6103 | -0.3277 | 9.0 | 0.08326 | 0.24978 | Not Significant |
| **Factual Grounding** | 30 | 9 | 2.167 [1.867, 2.433] | 2.400 [2.100, 2.667] | -0.233 [-0.400, -0.067] | 0.000 | 0.5040 | -0.4630 | 5.0 | 0.01963 | 0.07852 | Not Significant (after Holm) |

*Note on Factual Grounding*: While raw $p = 0.01963$ is below uncorrected $\alpha = 0.05$, it does not survive the Holm-Bonferroni threshold ($\alpha / 4 = 0.0125$) in the 5-metric family or ($\alpha / 2 = 0.025$) in the primary 3-metric family after controlling for family-wise error rate.

### 2.3 Out-of-Scope / Unsupported Handling (Panel B)

| Metric | Sample ($n$) | Non-Zero Pairs ($n_{\neq 0}$) | KG-RAG Mean [95% CI] | LLM-Only Mean [95% CI] | Paired Difference [95% CI] | Median Difference | SD ($d$) | Cohen's $d_z$ | Wilcoxon $W$ | Raw $p$ | Holm $p$ | Scientific Finding |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Unsupported Handling** | 6 | 3 | 2.167 [1.167, 2.833] | 1.333 [0.333, 2.500] | +0.833 [+0.167, +1.500] | +0.500 | 0.9832 | +0.8476 | 0.0 | 0.25000 | 0.25000 | **Exploratory Finding** (Directional advantage, $d_z = +0.85$) |

*Methodological Qualification*: On the 6 out-of-scope queries, KG-RAG demonstrated higher mean refusal and curriculum boundary adherence (+0.833 points), and the 95% bootstrap CI excludes zero [0.167, 1.500]. However, due to small sample size ($n=6, n_{\neq 0}=3$), the non-parametric Wilcoxon test yields $p = 0.25000$, which is non-significant. This is formally classified as an exploratory finding.

### 2.4 Gold-Fact Coverage Rate (Panel C)

| Metric | Sample ($n$) | Total Facts | KG-RAG Covered (Rate) | LLM-Only Covered (Rate) | Mean per-Question Difference [95% CI] | Wilcoxon $W$ | Raw $p$ | Holm $p$ | Significance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Gold-Fact Coverage** | 24 | 60 | 56 / 60 (93.3%) | 60 / 60 (100.0%) | -0.0694 [-0.1528, 0.000] | 0.0 | 0.10247 | 0.24978 | Not Significant |

- Per-question mean coverage: KG-RAG = 0.9306 (93.1%), LLM-Only = 1.0000 (100.0%).
- Non-zero paired differences: 3 of 24 supported questions (ADA: 10/10, CN: 9/10, DSA: 7/10, ML: 10/10, OS: 10/10, SEPM: 10/10; total 56/60).

### 2.5 Subject Breakdown in Human Audit ($n=5$ per Subject)

| Subject | Domain | KG-RAG Correctness | LLM-Only Correctness | KG-RAG Relevance | LLM-Only Relevance | KG-RAG Grounding | LLM-Only Grounding | KG-RAG Gold Facts | LLM-Only Gold Facts | Total Gold Facts |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADA** | Analysis & Design of Algorithms | 2.20 | 2.80 | 2.20 | 2.20 | 2.40 | 3.00 | 10 | 10 | 10 |
| **CN** | Computer Networks | 2.40 | 3.00 | 2.40 | 3.00 | 2.20 | 2.60 | 9 | 10 | 10 |
| **DSA** | Data Structures & Algorithms | 2.40 | 2.60 | 2.60 | 2.80 | 2.40 | 2.40 | 7 | 10 | 10 |
| **ML** | Machine Learning | 2.60 | 2.60 | 2.40 | 2.40 | 2.60 | 2.80 | 10 | 10 | 10 |
| **OS** | Operating Systems | 1.60 | 2.60 | 1.60 | 2.00 | 1.80 | 2.00 | 10 | 10 | 10 |
| **SEPM** | Software Eng. & Project Mgmt. | 1.60 | 2.00 | 1.80 | 1.80 | 1.60 | 1.60 | 10 | 10 | 10 |

---

## 3. Figure 4: Local Benchmark Latency Data ($N=120$)

### 3.1 Experimental Configuration
- **Total Questions**: $N=120$ paired queries ($240$ total execution runs).
- **Inference Engine**: Local Ollama runtime (`llama3.2:latest`, 3B parameter model).
- **Execution Environment**: Local consumer hardware workstation; deterministic seed 42; 4096 context token window.
- **Production Runtime Note**: Direct local benchmark evaluates consumer hardware overhead; cloud production API utilizes Groq LPUs (`llama-3.3-70b-versatile`) with millisecond-scale retrieval and generation.

### 3.2 Overall Latency Statistics (Panel A & Panel B)

| Metric | LLM-Only Baseline | EduGraphAI KG-RAG | Paired Difference (KG - LLM) | Relative Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Latency** | **20.190 s** | **47.294 s** | **+27.104 s** | **+134.2% increase** |
| **Latency Multiplier** | 1.00× | 2.34× | +1.34× | **2.34× factor** |
| **Standard Deviation ($SD$)** | 7.152 s (11.15 s overall) | 15.654 s (28.68 s overall) | 22.617 s | — |
| **Median Latency** | **17.18 s** (17.178 s) | **38.96 s** (38.962 s) | **+24.86 s** | +126.8% increase |
| **Interquartile Range (IQR)** | [14.60 s, 23.00 s] | [35.20 s, 54.10 s] | — | — |
| **Minimum Latency** | 1.380 s | 0.003 s (immediate refusal) | -23.760 s | — |
| **Maximum Latency** | 67.260 s | 207.773 s | +176.843 s | — |

### 3.3 Subject-Level Latency Breakdown ($n=20$ per Subject)

| Subject | Questions | LLM-Only Mean (s) | KG-RAG Mean (s) | Mean Difference (s) | LLM Median (s) | KG Median (s) | KG-RAG Retrieval Hit Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DSA** | 20 | 28.465 | 70.825 | +42.360 | 27.414 | 69.277 | 100% (16/16) |
| **OS** | 20 | 29.367 | 62.104 | +32.737 | 27.293 | 60.767 | 100% (16/16) |
| **ML** | 20 | 18.512 | 49.974 | +31.462 | 19.310 | 37.249 | 100% (16/16) |
| **ADA** | 20 | 16.153 | 37.879 | +21.726 | 15.906 | 38.791 | 100% (16/16) |
| **CN** | 20 | 13.958 | 34.098 | +20.140 | 15.031 | 33.853 | 100% (16/16) |
| **SEPM** | 20 | 14.685 | 28.884 | +14.199 | 14.105 | 27.288 | 100% (16/16) |

---

## 4. Figure 1 & Figure 2: Structural & Methodological Parameters

### 4.1 Figure 1: Architectural Parameters
- **Layer 1: Presentation & Client**: Next.js 14, React 18, Tailwind CSS, Interactive Canvas (`vis-network`), Structured Marking Breakdown (2/5/10 marks).
- **Layer 2: FastAPI Gateway & Services**: Endpoints `/api/query`, `/api/graph`, `/api/ask`; Topic and Intent Classification; Alias Normalization; Scope Validator.
- **Layer 3: Knowledge Graph Engine**: Neo4j Graph Database (managed AuraDB Cloud + Bolt local failover); 6 CS Subject Ontologies; 458 concept entities (497 curriculum edges); Multi-hop Cypher traversal (`IS_A`, `USES`, `PART_OF`).
- **Layer 4: Grounded Inference**: Dual-mode inference backend (Local Ollama llama3.2 3B; Cloud Groq llama-3.3 70B); deterministic temperature 0.2; context triples injection.
- **Layer 5: Educational Delivery**: Structured conceptual definitions; step-wise examination rubric; syllabus boundary guardrails; D3/Canvas rendered pedagogical subgraphs.

### 4.2 Figure 2: Evaluation Pipeline Architecture
- **Stage A (Full Automated Benchmark)**: Standardized dataset of $N=120$ questions (20 questions per subject across 6 subjects, 5 question categories); paired generation producing 240 responses; latency telemetry logging; automated LLM judge (phi4-mini) demonstrating positive leniency bias (+0.38 to +0.65).
- **Stage B (Double-Blind Human Quality Audit)**: Stratified representative sampling ($N=30$ pairs); blinded A/B order randomization with cryptographic mapping isolation; pre-registered rubric evaluation by human domain expert; non-parametric statistical hypothesis testing (Wilcoxon signed-rank, Holm-Bonferroni correction, 95% bootstrap CIs).

---

## 5. Verification & Consistency Audit Checklist

- [x] All numerical values in Figure 3 match `part_9k_validated_statistics.json` exactly.
- [x] 95% Bootstrap confidence intervals displayed on all metric bars.
- [x] Multiplicity correction explicitly labeled as Holm-Bonferroni adjusted $p$-values.
- [x] Statistical significance accurately noted: Correctness favors baseline ($p = 0.00875$); Relevance and Grounding are non-significant after correction.
- [x] Unsupported handling accurately characterized as exploratory ($n=6, p=0.250$).
- [x] Figure 4 latency metrics grounded in full $N=120$ benchmark distribution.
- [x] Local runtime (Ollama llama3.2 3B) clarified in footnotes to distinguish from cloud Groq production API.
- [x] Mandatory source attribution `"Source: EduGraphAI Part 9K validated evaluation"` present on all relevant figures.
- [x] All 4 generated figure images verified at $\ge 300$ DPI resolution.
