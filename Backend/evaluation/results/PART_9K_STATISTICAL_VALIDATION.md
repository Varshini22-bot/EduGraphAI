# Part 9K: Statistical Validation & Multiple-Comparison Correction Report

## 1. Purpose & Scope
This report documents the independent verification and statistical validation of the **Part 9J** evaluation results for the **EduGraphAI** research study. 
Part 9K independently evaluates:
- Implementation of standard `scipy.stats.wilcoxon` tests with two-sided hypotheses and explicit zero-difference treatment (`zero_method='wilcox'`).
- Multiple-comparison adjustment via the **Holm-Bonferroni step-down procedure** across all evaluated outcomes.
- Percentile bootstrap confidence intervals ($B=10,000$, seed=42).
- Paired effect sizes (Cohen's $d_z$) using sample standard deviation.
- Disentanglement of aggregate fact totals from question-level coverage rates.
- Re-evaluation of small-sample subsets (unsupported handling $n=6$, supported gold-fact coverage $n=24$).
- Strict separation of response latency ($N=120$) from human generation quality ($N=30$).

---

## 2. Authoritative Dataset Verification
- **Input Data**: [`human_evaluation_template.csv`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/human_evaluation_template.csv) (30 completed human blind evaluation records).
- **System Mapping**: [`blind_mapping.json`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/blind_mapping.json).
- **Verification**: Zero values were altered; zero records were added or removed. All 30 paired observations were verified against original double-blind records.

---

## 3. Statistical Methodology
- **Experimental Design**: Paired within-subjects design. Each query was independently answered by both systems and evaluated by a human domain researcher under double-blind conditions.
- **Hypothesis Testing**: Two-sided Wilcoxon signed-rank test implemented in SciPy 1.18.1 (`scipy.stats.wilcoxon(alternative='two-sided', zero_method='wilcox')`). Zero paired differences ($d_i = 0$) are pruned per standard Wilcoxon convention.
- **Multiple Comparison Correction**: Holm-Bonferroni method applied at family-wise error rate $\alpha = 0.05$ across all 5 evaluated outcomes, ordered by increasing raw $p$-values:
  `p_adjusted(i) = min(1, max_[k <= i] ((m - k + 1) * p_(k)))`
- **Confidence Intervals**: 95% Percentile Bootstrap confidence intervals computed over $B=10,000$ paired resamples with fixed seed 42.
- **Effect Size**: Cohen's $d_z = mean(d) / SD(d)$ with sample degrees of freedom ($ddof=1$).

---

## 4. Validated Statistical Results Table

### Table 1: Validated Statistical Comparison with Holm-Bonferroni Multiplicity Correction

| Metric | $n$ | KG-RAG Mean | LLM-Only Mean | Mean Diff ($d$) | Median Diff | 95% Bootstrap CI | Wilcoxon $W$ | Raw $p$ | Holm Adjusted $p$ | Effect Size ($d_z$) | Validated Conclusion ($\alpha = 0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Correctness** | 30 | 2.133 | 2.600 | $-0.467$ | $-0.500$ | $[-0.700, -0.233]$ | 17.0 | $0.00175$ | **$0.00875$** | $-0.685$ | **Statistically Significant** ($p < 0.01$) |
| **Educational Relevance** | 30 | 2.167 | 2.367 | $-0.200$ | $0.000$ | $[-0.433, +0.000]$ | 9.0 | $0.08326$ | $0.24978$ | $-0.328$ | Not Significant ($p = 0.25$) |
| **Factual Grounding** | 30 | 2.167 | 2.400 | $-0.233$ | $0.000$ | $[-0.400, -0.067]$ | 5.0 | $0.01963$ | $0.07852$ | $-0.463$ | **Not Significant After Holm Correction** |
| **Gold-Fact Coverage Rate** | 24 | 0.931 | 1.000 | $-0.069$ | $0.000$ | $[-0.153, +0.000]$ | 0.0 | $0.10247$ | $0.24978$ | $-0.366$ | Not Significant ($p = 0.25$) |
| **Unsupported Handling** | 6 | 2.167 | 1.333 | $+0.833$ | $+0.500$ | $[+0.167, +1.500]$ | 0.0 | $0.25000$ | $0.25000$ | $+0.848$ | **Exploratory Finding** (Not Significant, $p = 0.25$) |

*Notes:*
- Differences calculated as `KG-RAG - LLM-Only` (positive values favor KG-RAG; negative values favor LLM-Only).
- Raw $p$-values computed via SciPy `scipy.stats.wilcoxon(alternative='two-sided', zero_method='wilcox')`.
- Holm adjusted $p$-values computed across all 5 outcome tests using the Holm-Bonferroni step-down procedure.
- If evaluated strictly within the 3 primary metrics family, Factual Grounding adjusted $p = 0.03926$. However, across the full evaluation family of 5 outcomes, Factual Grounding yields adjusted $p = 0.07852$, failing to reject $H_0$ at $\alpha = 0.05$.

---

## 5. Critical Statistical Corrections to Part 9J

### 5.1 Factual Grounding Interpretation Correction
- **Part 9J Statement**: Claimed Factual Grounding was statistically significant ($p = 0.0391 < 0.05$).
- **Validated Finding**: While raw unadjusted $p = 0.01963$ (SciPy asymptotic) or $p = 0.03906$ (exact permutation), the **Holm-Bonferroni adjusted $p$-value across the 5 tested outcomes is $p = 0.07852 > 0.05$**.
- **Correction**: After multiplicity correction, the difference in factual grounding is **not statistically significant** at the $\alpha = 0.05$ threshold. The observed difference (LLM-Only mean 2.400 vs KG-RAG mean 2.167) represents a descriptive divergence that cannot be claimed as statistically robust under rigorous family-wise error control.

### 5.2 Unsupported-Topic Handling Reclassification ($n=6$)
- **Part 9J Statement**: Highlighted a "large effect ($d_z = +0.85$, CI > 0)" and emphasized positive bound of bootstrap CI.
- **Validated Finding**: The subset consists of only $n=6$ items, with only $N_r=3$ non-zero paired differences. The exact Wilcoxon test yields $p = 0.25000$. Under Holm correction, $p_Holm = 0.25000 > 0.05$.
- **Correction**: A bootstrap confidence interval that excludes zero cannot substitute for hypothesis testing. The unsupported-topic result must be strictly characterized as an **exploratory descriptive finding** rather than a statistically confirmed effect. While KG-RAG demonstrated a notable directional mean advantage (+0.833 points) in adhering to syllabus boundaries, the sample size ($n=6$) is underpowered for confirmatory inferential claims.

### 5.3 Gold-Fact Semantic Coverage Clarification ($n=24$)
- **Clarification**: Two distinct coverage metrics must be reported without conflation:
  1. **Aggregate Fact Count**: KG-RAG covered **56 / 60 reference facts (93.3%)**; LLM-Only covered **60 / 60 reference facts (100.0%)**.
  2. **Question-Level Mean Coverage Rate**: KG-RAG mean question rate was **0.9306 (93.1%)** (median 1.000); LLM-Only mean question rate was **1.0000 (100.0%)** (median 1.000).
  3. **Hypothesis Test**: Paired Wilcoxon test on question-level rates ($n=24, N_r=3$ non-zero differences) yields raw $p = 0.10247$ (SciPy auto) / $p = 0.25000$ (exact permutation), and Holm-adjusted $p = 0.24978$. There is **no statistically significant difference** in gold-fact coverage between the two systems.

---

## 6. Subject-Level Descriptive Breakdown ($N=5$ per Subject)
*Note: Due to small sample size ($n=5$ per subject), these statistics are strictly descriptive.*

| Subject | KG-RAG Correctness | LLM-Only Correctness | KG-RAG Relevance | LLM-Only Relevance | KG-RAG Grounding | LLM-Only Grounding | KG-RAG Gold Facts | LLM-Only Gold Facts | Total Gold Facts |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADA** | 2.2 | 2.8 | 2.2 | 2.2 | 2.4 | 3.0 | 10 | 10 | 10 |
| **CN** | 2.4 | 3.0 | 2.4 | 3.0 | 2.2 | 2.6 | 9 | 10 | 10 |
| **DSA** | 2.4 | 2.6 | 2.6 | 2.8 | 2.4 | 2.4 | 7 | 10 | 10 |
| **ML** | 2.6 | 2.6 | 2.4 | 2.4 | 2.6 | 2.8 | 10 | 10 | 10 |
| **OS** | 1.6 | 2.6 | 1.6 | 2.0 | 1.8 | 2.0 | 10 | 10 | 10 |
| **SEPM** | 1.6 | 2.0 | 1.8 | 1.8 | 1.6 | 1.6 | 10 | 10 | 10 |

---

## 7. Category-Level Descriptive Breakdown ($N=6$ per Category)
*Note: Descriptive analysis across question categories ($n=6$).*

| Category | KG-RAG Correctness | LLM-Only Correctness | Diff Correctness | KG-RAG Relevance | LLM-Only Relevance | Diff Relevance | KG-RAG Grounding | LLM-Only Grounding | Diff Grounding |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **factual** | 2.667 | 2.667 | +0.000 | 2.333 | 2.333 | +0.000 | 2.667 | 2.667 | +0.000 |
| **conceptual** | 2.5 | 2.667 | -0.167 | 2.833 | 2.667 | +0.167 | 2.5 | 2.667 | -0.167 |
| **comparison** | 2.333 | 3.0 | -0.667 | 2.0 | 2.333 | -0.333 | 2.167 | 2.5 | -0.333 |
| **relationship** | 1.667 | 2.5 | -0.833 | 2.0 | 2.333 | -0.333 | 1.833 | 2.167 | -0.333 |
| **unsupported** | 1.5 | 2.167 | -0.667 | 1.667 | 2.167 | -0.500 | 1.667 | 2.0 | -0.333 |

---

## 8. Latency Analysis (Separated Full Benchmark, $N=120$)
- **Sample Size**: $N=120$ benchmark questions.
- **LLM-Only Latency**: Mean 20.19 s ($SD = 7.152 s$)
- **KG-RAG Latency**: Mean 47.294 s ($SD = 15.654 s$)
- **Paired Mean Difference**: +27.104 s
- **Latency Ratio**: $2.34x$ slower for KG-RAG.
- **Distinction**: Latency was measured across all 120 benchmark runs and must not be conflated with the 30-question human evaluation sample.

---

## 9. Summary of Validated Research Claims
1. **Confirmatory Statistical Finding**: The LLM-only baseline scored higher in human Correctness than KG-RAG (2.6 vs 2.1333; difference $-0.467$, Holm-adjusted $p = 0.00875$). This statistically significant result reflects the greater stylistic fluency and unconstrained elaboration of the base LLM on small local models (`llama3.2`).
2. **Non-Significant Findings**: Educational Relevance (Holm $p = 0.24978$), Factual Grounding (Holm $p = 0.07852$), and Gold-Fact Coverage (Holm $p = 0.24978$) showed no statistically significant differences between the two systems after multiplicity correction.
3. **Exploratory Finding**: On unsupported curriculum queries ($n=6$), KG-RAG exhibited a higher mean score (+0.833 points) in refusing out-of-scope topics. However, with $N_r=3$ non-zero pairs and $p = 0.25000$, this observation is exploratory and requires larger sample replication.
