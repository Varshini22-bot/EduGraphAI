# EduGraphAI Blinded Human Evaluation Guide

## 1. Purpose of the Evaluation
This guide specifies the standardized protocol for evaluating answer quality in the research comparison between **LLM-only baseline** and **EduGraphAI Knowledge Graph-RAG (KG-RAG)**.

The benchmark contains **120 questions** across 6 core undergraduate Computer Science subjects:
* **DSA** (Data Structures & Algorithms)
* **ADA** (Analysis & Design of Algorithms)
* **CN** (Computer Networks)
* **ML** (Machine Learning)
* **OS** (Operating Systems)
* **SEPM** (Software Engineering & Project Management)

Across these subjects, the benchmark evaluates:
* **96 supported questions** across 4 categories: `factual`, `conceptual`, `comparison`, and `relationship`.
* **24 unsupported questions**: out-of-scope questions designed to test curriculum boundary awareness.

---

## 2. Blind A/B Experimental Setup
* For each question, two candidate answers are presented: **Answer A** and **Answer B**.
* System identities are randomized independently for every question and kept in a secure, isolated key file (`blind_mapping.json`).
* **CRITICAL INSTRUCTION**: Evaluators must **NOT** attempt to guess, deduce, or infer which system produced Answer A or Answer B. Do not look for stylistic quirks or length differences to identify systems. Evaluate both answers strictly on their objective academic merit.

---

## 3. Evaluation Dimensions & Scoring Rubric

All ordinal metrics are scored on a discrete **0 to 3 scale**.

### Dimension 1: Correctness (0 to 3)
Measures the academic and conceptual accuracy of computer science definitions, algorithms, and complexity claims.

* **Score 0 (Incorrect / Misleading)**: Contains fundamental conceptual falsehoods, invalid formulas, or misleading technical explanations.
* **Score 1 (Major Errors / Limited Truth)**: Contains major technical flaws, incorrect asymptotic bounds, or only brief fragments of accurate information surrounded by errors.
* **Score 2 (Mostly Correct)**: Technically accurate overall, with only minor non-critical omissions, slight mathematical imprecision, or negligible wording ambiguities.
* **Score 3 (Fully Correct)**: Completely accurate, conceptually sound, academically rigorous, and free from errors.

### Dimension 2: Educational Relevance (0 to 3)
Measures how directly, clearly, and thoroughly the response addresses the prompt in the context of university undergraduate examinations.

* **Score 0 (Irrelevant / Off-topic)**: Completely fails to address the question asked.
* **Score 1 (Weakly Related)**: Addresses marginal tangents while failing to engage with the primary concept or inquiry.
* **Score 2 (Relevant)**: Addresses the main question clearly and covers primary pedagogical expectations with minor unnecessary elaboration.
* **Score 3 (Directly & Appropriately Relevant)**: Focuses directly on the core question, structured appropriately for undergraduate examination standards.

### Dimension 3: Factual Grounding (0 to 3)
Measures whether factual claims are substantiated by verified curriculum knowledge rather than speculative hallucinations.

* **Protocol for Evaluators**: In a blind evaluation, evaluators verify assertions against established standard textbook domain facts. Do **NOT** automatically penalize an answer simply because it does not cite graph metadata.
* **Score 0 (Ungrounded / Hallucinatory)**: Invents non-existent protocols, algorithms, syntax, or theoretical properties.
* **Score 1 (Weakly Grounded)**: Makes claims that are dubious or unsubstantiated in undergraduate curricula alongside sporadic true statements.
* **Score 2 (Substantially Grounded)**: Key claims and foundational properties match established syllabus standards.
* **Score 3 (Fully Grounded)**: All assertions, examples, and relationship descriptions are fully verifiable and grounded in established computer science theory.

### Dimension 4: Gold-Fact Coverage (Proportion)
For each supported question, `eval_dataset.json` specifies explicit **gold reference facts**.
* **`gold_fact_total`**: The pre-populated count of required facts.
* **`gold_fact_covered_A` / `gold_fact_covered_B`**: The number of gold facts whose underlying semantic proposition is accurately reflected in the candidate answer.
* **Rule**: Do **NOT** use naive substring or exact word matching. Credit a fact if the semantic meaning and conceptual proposition are clearly conveyed.

### Dimension 5: Unsupported Handling (0 to 3)
Evaluated **only** on the 24 out-of-scope questions (`is_supported = false`). For supported questions, leave blank or record `N/A`.

* **Score 0 (Hallucinated In-Scope)**: Confidently explains the topic as though it belongs to the standard 6-subject curriculum without any scope awareness.
* **Score 1 (Weak Hedging)**: Notes some vagueness or unfamiliarity but still proceeds to offer a full ungrounded answer.
* **Score 2 (Substantial Boundary Awareness)**: Notes syllabus limitations or scope boundaries, but exhibits slight ambiguity in handling.
* **Score 3 (Exemplary Boundary Refusal)**: Explicitly recognizes the topic as outside the supported curriculum boundaries and provides a courteous, helpful refusal directing the user to valid syllabus subjects.

---

## 4. Special Cases & Guidelines

1. **Partially Correct Answers**:
   * If an answer gets the asymptotic complexity right ($O(\log n)$) but gives an incorrect rotation rule, assign a Correctness score of `2` (mostly correct with minor error) rather than `1` or `3`.
2. **Answers with Extra but Correct Information**:
   * If an answer provides additional accurate technical details (e.g., historical context, alternative algorithmic implementations), do **NOT** penalize its Correctness. If the extra content detracts significantly from clarity, reduce the Relevance score from `3` to `2`.
3. **Handling Evaluator Uncertainty**:
   * If an evaluator is uncertain about an advanced topic or nuance, record the uncertainty in the `evaluator_notes` column rather than guessing.
4. **Consistency**:
   * Evaluate Answer A and Answer B under identical scrutiny. Do not evaluate one leniently and the other strictly.

---

## 5. Completing the Template
* Open [`human_evaluation_template.csv`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/human_evaluation_template.csv).
* For each row (`EVAL_001` through `EVAL_120`), enter numeric scores (0 to 3) in the respective columns.
* Save the completed spreadsheet as `human_evaluation_completed.csv`.
