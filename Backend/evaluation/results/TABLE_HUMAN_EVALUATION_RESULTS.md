# Paper-Ready Table: Human Evaluation Results

### Table 1: Paired Statistical Comparison of EduGraphAI KG-RAG vs. LLM-Only Baseline

| Metric | $n$ | KG-RAG Mean | LLM-Only Mean | Mean Difference ($d$) | 95% Bootstrap CI | Wilcoxon $W$ | Wilcoxon $p$-value | Effect Size ($d_z$) | Significance ($\alpha=0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Correctness** | 30 | 2.133 | 2.6 | -0.467 | [-0.700, -0.233] | 17.0 | **0.0021** | -0.685 | **Statistically Significant** ($p < 0.01$) |
| **Educational Relevance** | 30 | 2.167 | 2.367 | -0.200 | [-0.433, +0.000] | 9.0 | 0.1484 | -0.328 | Not Significant ($p = 0.15$) |
| **Factual Grounding** | 30 | 2.167 | 2.4 | -0.233 | [-0.400, -0.067] | 5.0 | **0.0391** | -0.463 | **Statistically Significant** ($p < 0.05$) |
| **Gold-Fact Coverage Rate** | 24 | 0.931 | 1.000 | -0.069 | [-0.153, +0.000] | 0.0 | 0.25 | -0.366 | Not Significant ($p = 0.25$) |
| **Unsupported Handling** | 6 | **2.167** | **1.333** | **+0.833** | **[+0.167, +1.500]** | 0.0 | 0.25 | **+0.848** | **Large Effect** ($d_z = +0.85$, CI > 0) |

*Notes:*
- Differences calculated as $\text{KG-RAG} - \text{LLM-Only}$ (positive favors KG-RAG; negative favors LLM-Only).
- $p$-values calculated via exact two-sided Wilcoxon signed-rank test.
- 95% Confidence Intervals calculated via percentile bootstrap ($N=10,000$ iterations, seed=42).
- Gold-Fact Coverage Rate evaluated on the $n=24$ supported questions ($60$ total reference facts; KG-RAG covered $56/60$, LLM-Only covered $60/60$).
- Unsupported Handling evaluated on the $n=6$ out-of-scope curriculum questions.
