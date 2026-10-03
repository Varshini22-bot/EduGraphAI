# Results Section (Validated Manuscript Draft)

## Experimental Evaluation

We evaluated EduGraphAI against an unaugmented LLM-only baseline across 120 standardized computer science examination questions spanning six academic subjects (ADA, CN, DSA, ML, OS, and SEPM). To assess generation quality under rigorous conditions, a stratified 30-question subset (24 supported syllabus questions and 6 out-of-scope questions) was evaluated by a domain researcher in a double-blind protocol using a validated 0–3 rubric across Correctness, Educational Relevance, Factual Grounding, Gold-Fact Coverage, and Unsupported Topic Handling.

### Statistical Analysis & Multiple-Comparison Correction
Paired differences were evaluated using two-sided Wilcoxon signed-rank tests with zero-difference pruning (`zero_method='wilcox'`). To control family-wise error across the evaluated outcomes, $p$-values were adjusted using the Holm-Bonferroni step-down procedure at $$\alpha = 0.05$$. In addition, 95% confidence intervals were estimated using percentile bootstrap resampling ($B=10,000$ iterations), and paired effect sizes were computed using Cohen's $d_z$.

### Quality Evaluation Results
Table 1 presents the validated statistical comparison between EduGraphAI KG-RAG and the LLM-only baseline.

On the primary metric of **Correctness**, the LLM-only baseline achieved a higher mean rating than KG-RAG (2.600 vs. 2.133; paired mean difference $d = -0.467$, 95% bootstrap CI [-0.700, -0.233], Wilcoxon $W = 17.0, p = 0.0018$, Holm-adjusted $p = 0.0088, d_z = -0.685$). This difference remained statistically significant after multiple-comparison correction ($p < 0.01$). This outcome is attributable to the base generator (`llama3.2`) producing more elaborative and fluent prose when unconstrained by graph retrieval context, whereas KG-RAG responses were more concise and included conservative refusals.

On **Educational Relevance**, both systems maintained comparable pedagogical alignment (2.167 for KG-RAG vs. 2.367 for LLM-Only; paired mean difference $d = -0.200$, Wilcoxon $W = 9.0, p = 0.0833$, Holm-adjusted $p = 0.2498$). The difference was not statistically significant.

On **Factual Grounding**, although an unadjusted test showed a modest descriptive difference favoring the baseline (2.400 vs. 2.167; raw $p = 0.0196$), this difference was **not statistically significant following Holm-Bonferroni correction** (Holm-adjusted $p = 0.0785 > 0.05$; 95% bootstrap CI [-0.400, -0.067]).

### Factual Coverage on Supported Curriculum ($n=24$)
Across the 24 supported curriculum queries (encompassing 60 total reference gold facts), both systems achieved near-ceiling semantic coverage. The LLM-only baseline covered 60 / 60 facts (100.0%, mean question rate 1.000), while KG-RAG covered 56 / 60 facts (93.3%, mean question rate 0.931). The paired difference was not statistically significant (Wilcoxon $W = 0.0, p = 0.1025$, Holm-adjusted $p = 0.2498$).

### Unsupported Topic Handling ($n=6$, Exploratory)
For the 6 out-of-scope curriculum questions, KG-RAG achieved a higher descriptive mean rating in recognizing syllabus boundaries and providing appropriate refusals (2.167 vs. 1.333; paired mean difference $d = +0.833$, Cohen's $d_z = +0.85$, 95% bootstrap CI [+0.167, +1.500]). However, because only $N_r = 3$ non-zero paired differences were observed in this small subset, the non-parametric hypothesis test did not achieve statistical significance (Wilcoxon $W = 0.0, p = 0.2500$, Holm-adjusted $p = 0.2500$). This finding is therefore characterized as an exploratory observation indicating directional guardrail enforcement that warrants larger-sample study.

### Response Latency ($N=120$)
Across the full 120-question benchmark, KG-RAG exhibited an average response latency of 47.29 s ($SD = 15.65$ s), compared to 20.19 s ($SD = 7.15$ s) for the LLM-only baseline (paired mean difference +27.10 s, representing a 2.34$x$ factor). This latency overhead reflects the multi-hop Cypher traversal and structured graph context assembly executing on local hardware.

### Evaluation Limitations
This evaluation was conducted using a local 3-billion-parameter language model (`llama3.2`) and a human audit sample of 30 questions. While the audit provides high-fidelity double-blind validation, the modest sample sizes in the unsupported ($n=6$) and subject-level ($n=5$) subsets limit the statistical power for subgroup confirmatory inference.
