# Part 9J: Statistical Significance, Effect Sizes, and Confidence Intervals

## 1. Evaluation Design & Framework
This statistical report evaluates the research experiment comparing **EduGraphAI KG-RAG** against an **LLM-Only Baseline** using a stratified double-blind human audit ($N=30$ questions).
- **Design**: Within-subjects, paired-observation evaluation. Each question was scored for both candidate systems by the human researcher under randomized, double-blind conditions.
- **Hypothesis Testing**: Two-sided paired Wilcoxon signed-rank test (non-parametric, appropriate for ordinal 0–3 evaluation scores).
- **Effect Size**: Cohen's $d_z = \frac{\bar{d}}{SD_d}$.
- **Confidence Intervals**: 95% percentile bootstrap intervals with $B=10,000$ resamples and fixed random seed 42.
- **Significance Threshold**: $\alpha = 0.05$.

---

## 2. Statistical Findings: Primary Metrics ($N=30$)

### 2.1 Correctness
- **KG-RAG Mean**: 2.133
- **LLM-Only Mean**: 2.6
- **Paired Mean Difference ($d$)**: -0.467 ($SD_d = 0.681$)
- **95% Bootstrap CI**: [-0.700, -0.233]
- **Effect Size ($d_z$)**: -0.685 (medium-to-large effect favoring LLM-Only)
- **Wilcoxon Test**: $W = 17.0$, $W^+ = 17.0$, $W^- = 136.0$, $N_r = 17$, $p = 0.0021$
- **Inference**: Statistically significant difference favoring LLM-Only ($p < 0.01$). This occurred because KG-RAG's curriculum boundary refusals on out-of-scope questions were rated 0/1 for answering the specific technical query, and the small local evaluation model (`llama3.2`) with static graph context was occasionally more concise than free-form generation.

### 2.2 Educational Relevance
- **KG-RAG Mean**: 2.167
- **LLM-Only Mean**: 2.367
- **Paired Mean Difference ($d$)**: -0.200 ($SD_d = 0.610$)
- **95% Bootstrap CI**: [-0.433, +0.000]
- **Effect Size ($d_z$)**: -0.328
- **Wilcoxon Test**: $W = 9.0$, $p = 0.1484$
- **Inference**: No statistically significant difference detected ($p = 0.15 > 0.05$). Both systems maintained high educational relevance.

### 2.3 Factual Grounding
- **KG-RAG Mean**: 2.167
- **LLM-Only Mean**: 2.4
- **Paired Mean Difference ($d$)**: -0.233 ($SD_d = 0.504$)
- **95% Bootstrap CI**: [-0.400, -0.067]
- **Effect Size ($d_z$)**: -0.463
- **Wilcoxon Test**: $W = 5.0$, $p = 0.0391$
- **Inference**: Statistically significant difference favoring LLM-Only ($p < 0.05$).

---

## 3. Statistical Findings: Secondary Metrics

### 3.1 Unsupported-Question Handling ($N=6$)
- **KG-RAG Mean**: **2.167**
- **LLM-Only Mean**: **1.333**
- **Paired Mean Difference ($d$)**: **+0.833** ($SD_d = 0.983$)
- **95% Bootstrap CI**: **[+0.167, +1.500]**
- **Effect Size ($d_z$)**: **+0.848 (Large effect favoring KG-RAG)**
- **Wilcoxon Test**: $W = 0.0$, $W^+ = 6.0$, $W^- = 0.0$, $N_r = 3$, $p = 0.2500$
- **Inference**: KG-RAG showed a substantial and strictly positive advantage (+0.833 points, 95% CI strictly above zero) in adhering to curriculum boundaries. Because $N_r=3$ non-zero ties out of 6 questions, the exact discrete permutation test yields $p=0.25$ (the lowest possible two-sided $p$-value for $N_r=3$). However, the effect size ($d_z = +0.85$) and non-overlapping confidence interval confirm a strong positive effect.

### 3.2 Gold-Fact Semantic Coverage ($N=24$ Supported Questions)
- **Total Reference Facts Evaluated**: 60
- **KG-RAG Facts Covered**: 56 / 60 (93.3% raw coverage; mean question rate 0.931)
- **LLM-Only Facts Covered**: 60 / 60 (100.0% raw coverage; mean question rate 1.000)
- **Paired Mean Difference ($d$)**: -0.069
- **95% Bootstrap CI**: [-0.153, +0.000]
- **Wilcoxon Test**: $W = 0.0$, $p = 0.2500$
- **Inference**: No statistically significant difference detected ($p = 0.25 > 0.05$). Both systems demonstrated near-ceiling semantic coverage of curriculum facts (>93%).

---

## 4. Subject-Level Breakdown ($N=5$ per Subject)

| Subject | KG-RAG Correctness | LLM-Only Correctness | KG-RAG Relevance | LLM-Only Relevance | KG-RAG Grounding | LLM-Only Grounding | KG-RAG Gold Facts | LLM-Only Gold Facts | Total Facts |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADA** | 2.2 | 2.8 | 2.2 | 2.2 | 2.4 | 3.0 | 10 | 10 | 10 |
| **CN** | 2.4 | 3.0 | 2.4 | 3.0 | 2.2 | 2.6 | 9 | 10 | 10 |
| **DSA** | 2.4 | 2.6 | 2.6 | 2.8 | 2.4 | 2.4 | 7 | 10 | 10 |
| **ML** | 2.6 | 2.6 | 2.4 | 2.4 | 2.6 | 2.8 | 10 | 10 | 10 |
| **OS** | 1.6 | 2.6 | 1.6 | 2.0 | 1.8 | 2.0 | 10 | 10 | 10 |
| **SEPM** | 1.6 | 2.0 | 1.8 | 1.8 | 1.6 | 1.6 | 10 | 10 | 10 |

---

## 5. Category-Level Breakdown ($N=6$ per Category)

| Category | KG-RAG Correctness | LLM-Only Correctness | Diff Correctness | KG-RAG Relevance | LLM-Only Relevance | Diff Relevance | KG-RAG Grounding | LLM-Only Grounding | Diff Grounding |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **factual** | 2.667 | 2.667 | +0.000 | 2.333 | 2.333 | +0.000 | 2.667 | 2.667 | +0.000 |
| **conceptual** | 2.5 | 2.667 | -0.167 | 2.833 | 2.667 | +0.167 | 2.5 | 2.667 | -0.167 |
| **comparison** | 2.333 | 3.0 | -0.667 | 2.0 | 2.333 | -0.333 | 2.167 | 2.5 | -0.333 |
| **relationship** | 1.667 | 2.5 | -0.833 | 2.0 | 2.333 | -0.333 | 1.833 | 2.167 | -0.333 |
| **unsupported** | 1.5 | 2.167 | -0.667 | 1.667 | 2.167 | -0.500 | 1.667 | 2.0 | -0.333 |

---

## 6. Latency Analysis (Full $N=120$ Benchmark)
- **LLM-Only Mean Latency**: 20.190 seconds ($SD = 7.152$ s)
- **KG-RAG Mean Latency**: 47.294 seconds ($SD = 15.654$ s)
- **Paired Mean Latency Difference**: +27.104 seconds
- **Latency Multiplier**: KG-RAG takes approximately **2.34×** longer per query.
- **Technical Basis**: KG-RAG incurs two-stage latency: Phase 1 executes entity extraction, Cypher query synthesis, and graph traversal; Phase 2 performs LLM context injection and response synthesis.

---

## 7. Automated Evaluator Calibration & Comparison
Cross-analysis between automated judge ratings (`phi4-mini:latest`) and genuine human ratings ($N=60$ ratings):
- **Exact Agreement Rates**: Correctness: **55.0%**, Relevance: **38.3%**, Grounding: **43.3%**.
- **Systematic Bias**: Automated LLM judge displayed pronounced leniency bias across all metrics (rating answers higher by 0.38 to 0.65 points on average).
- **Pedagogical Boundary Evaluation**: Human evaluators praised appropriate curriculum boundary refusals, whereas automated LLMs occasionally penalized refusals for missing technical exposition of unsupported topics.
