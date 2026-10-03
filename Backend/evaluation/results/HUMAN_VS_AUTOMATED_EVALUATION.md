# EduGraphAI — Human Evaluator vs Automated LLM Evaluator Comparison

## 1. Methodological Disclaimer
This report compares **genuine human ratings** against **automated LLM evaluation ratings** (`phi4-mini:latest`).
**Automated LLM evaluations must NOT be treated as human ground truth.** Automated models frequently exhibit leniency bias and difficulty assessing concise domain boundary refusals.

---

## 2. Agreement & Score Calibration Metrics ($N=60$ Answer Ratings)

| Metric | Exact Score Agreement | Agreement Rate (%) | Mean Calibration Difference (Human - Automated) | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **Correctness** | 33 / 60 | **55.0%** | **-0.383** | Automated judge scored higher than human (Leniency bias) |
| **Relevance** | 23 / 60 | **38.3%** | **-0.650** | Automated judge awarded near-perfect relevance scores |
| **Grounding** | 26 / 60 | **43.3%** | **-0.567** | Human evaluator applied stricter standards for claims |

---

## 3. Key Divergence Patterns
1. **Leniency Bias in Automated Evaluator**:
   - The automated LLM judge rated answers systematically higher across all three metrics by 0.38 to 0.65 points.
   - Human evaluators were more discriminating regarding subtle omissions and technical errors.
2. **Handling of Boundary Refusals**:
   - In `EVAL_099` and `EVAL_117`, the human evaluator awarded score 3 for proper curriculum boundary refusals, recognizing appropriate pedagogical behavior.
   - The automated judge occasionally penalized boundary refusals on correctness because no technical explanation of the out-of-scope concept was provided.
