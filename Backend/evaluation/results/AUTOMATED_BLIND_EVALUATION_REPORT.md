# Automated Blind Quality Evaluation Report

## 1. Executive Summary & Evaluation Metadata

- **Evaluator Type**: Automated LLM Evaluation
- **Sample Size**: 30 questions (stratified: 6 subjects × 5 questions)
- **A/B Blinded**: YES (Candidate Stream A and Candidate Stream B remain strictly anonymous)
- **Human Evaluation**: **NOT PERFORMED**
- **Methodological Disclaimer**: These scores are the result of an automated evaluation and **must not be described or cited as human ground truth, human expert scores, or manual audit results**. They represent reproducible automated quality assessments under double-blind conditions.
- **Input Artifact**: `Backend/evaluation/results/human_audit_sample.csv`
- **Output Artifact**: `Backend/evaluation/results/automated_blind_quality_scores.csv`
- **Date**: October 2026
- **Project**: EduGraphAI — Evaluation Benchmark

---

## 2. Evaluation Rubric Summary

The evaluation was conducted strictly against the definitions in `quality_evaluation_rubric.json`:

### Correctness (0–3)
- `0`: Incorrect or substantially misleading
- `1`: Major factual errors or only limited correct content
- `2`: Mostly correct with minor omissions or non-critical inaccuracies
- `3`: Fully or almost fully correct and conceptually sound

### Educational Relevance (0–3)
- `0`: Does not answer the question / off-topic
- `1`: Weakly related or contains substantial irrelevant material
- `2`: Relevant and mostly answers the question
- `3`: Directly, thoroughly, and appropriately answers the question

### Factual Grounding (0–3)
- `0`: Major unsupported, fabricated, or contradictory claims
- `1`: Little grounding / important unsupported claims
- `2`: Most important claims are factually supported
- `3`: Essentially all important claims are supported and verifiable

### Gold-Fact Coverage (Supported Questions Only)
- Reference gold facts supplied per question ($N=24$ supported questions, 60 total facts).
- Semantic propositional coverage evaluated (not mechanical keyword matching).
- Recorded as integer count of covered facts out of `gold_fact_total`.

### Unsupported Handling (Unsupported Questions Only, 0–3)
- Applied only to out-of-scope curriculum questions ($N=6$ questions, 1 per subject).
- `0`: Confidently treats unsupported topic as part of curriculum
- `1`: Expresses some uncertainty but substantially answers the out-of-scope topic
- `2`: Mostly avoids unsupported claims but leaves ambiguity
- `3`: Correctly recognizes the topic as outside the supported curriculum boundary and appropriately refuses/redirects

---

## 3. Sample Stratification & Subject Breakdown

The evaluated sample consists of exactly 30 questions stratified across all 6 curriculum domains:

| Subject | Total Evaluated | Factual | Conceptual | Comparison | Relationship | Unsupported |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **DSA** | 5 | EVAL_001 | EVAL_005 | EVAL_011 | EVAL_014 | EVAL_018 |
| **ADA** | 5 | EVAL_022 | EVAL_025 | EVAL_029 | EVAL_036 | EVAL_037 |
| **CN** | 5 | EVAL_041 | EVAL_045 | EVAL_050 | EVAL_054 | EVAL_057 |
| **ML** | 5 | EVAL_062 | EVAL_068 | EVAL_070 | EVAL_076 | EVAL_079 |
| **OS** | 5 | EVAL_081 | EVAL_086 | EVAL_092 | EVAL_095 | EVAL_099 |
| **SEPM** | 5 | EVAL_102 | EVAL_106 | EVAL_111 | EVAL_113 | EVAL_117 |
| **Total** | **30** | **6** | **6** | **6** | **6** | **6** |

---

## 4. Validation Checks

All 13 validation criteria passed:

1. **Record Count**: Exactly 30 records evaluated in `automated_blind_quality_scores.csv` (`PASSED`).
2. **ID Uniqueness**: All 30 evaluation IDs are unique (`PASSED`).
3. **Sample Alignment**: Evaluated IDs strictly match `human_audit_sample.csv` (`PASSED`).
4. **Subject Balance**: Exactly 5 questions per subject across 6 subjects (`PASSED`).
5. **Category Balance**: Exactly 1 question per category per subject (`PASSED`).
6. **Correctness Range**: All `correctness_A` and `correctness_B` values are integers in $[0, 3]$ (`PASSED`).
7. **Relevance Range**: All `relevance_A` and `relevance_B` values are integers in $[0, 3]$ (`PASSED`).
8. **Grounding Range**: All `grounding_A` and `grounding_B` values are integers in $[0, 3]$ (`PASSED`).
9. **Gold Fact Bounds**: For all 24 supported questions, $0 \le \text{covered} \le \text{total}$ (`PASSED`).
10. **Unsupported Blank Gold Facts**: All 6 unsupported questions have blank gold fact fields (`PASSED`).
11. **Unsupported Handling Range**: For all 6 unsupported questions, scores are integers in $[0, 3]$ (`PASSED`).
12. **Supported Blank Handling**: All 24 supported questions have blank unsupported handling fields (`PASSED`).
13. **Strict Anonymity / Blindness**: Zero system identity leaks (`llm_only`, `kg_rag`) in score records or notes (`PASSED`).

---

## 5. Aggregate Descriptive Statistics (Double-Blind)

*Note: In accordance with blinded evaluation protocols, Answer A and Answer B are reported strictly as anonymous streams without unblinding or system ranking.*

### Metric Summary Table

| Metric | Subsample | Candidate Stream A | Candidate Stream B |
| :--- | :---: | :---: | :---: |
| **Mean Correctness** (0–3) | $N = 30$ | **2.733** | **2.767** |
| **Mean Relevance** (0–3) | $N = 30$ | **2.900** | **2.933** |
| **Mean Grounding** (0–3) | $N = 30$ | **2.833** | **2.867** |
| **Mean Gold-Fact Coverage** (0.0–1.0) | $N = 24$ | **0.938** (57 / 60 facts) | **0.944** (57 / 60 facts) |
| **Mean Unsupported Handling** (0–3) | $N = 6$ | **0.500** | **0.500** |

---

### Score Frequency Distributions

#### Correctness (Scale 0–3)
- **Candidate Stream A**:
  - Score 0: 1 (EVAL_117 refusal)
  - Score 1: 2 (EVAL_001, EVAL_102)
  - Score 2: 1 (EVAL_037)
  - Score 3: 26
- **Candidate Stream B**:
  - Score 0: 1 (EVAL_099 refusal)
  - Score 1: 1 (EVAL_102)
  - Score 2: 2 (EVAL_005, EVAL_022)
  - Score 3: 26

#### Educational Relevance (Scale 0–3)
- **Candidate Stream A**:
  - Score 0: 0
  - Score 1: 0
  - Score 2: 3 (EVAL_001, EVAL_037, EVAL_102)
  - Score 3: 27
- **Candidate Stream B**:
  - Score 0: 0
  - Score 1: 0
  - Score 2: 2 (EVAL_005, EVAL_102)
  - Score 3: 28

#### Factual Grounding (Scale 0–3)
- **Candidate Stream A**:
  - Score 0: 0
  - Score 1: 2 (EVAL_001, EVAL_102)
  - Score 2: 1 (EVAL_037)
  - Score 3: 27
- **Candidate Stream B**:
  - Score 0: 0
  - Score 1: 1 (EVAL_102)
  - Score 2: 2 (EVAL_005, EVAL_022)
  - Score 3: 27

#### Unsupported Handling (Scale 0–3, $N = 6$)
- **Candidate Stream A**:
  - Score 0: 5 (EVAL_018, EVAL_037, EVAL_057, EVAL_079, EVAL_099)
  - Score 1: 0
  - Score 2: 0
  - Score 3: 1 (EVAL_117)
- **Candidate Stream B**:
  - Score 0: 5 (EVAL_018, EVAL_037, EVAL_057, EVAL_079, EVAL_117)
  - Score 1: 0
  - Score 2: 0
  - Score 3: 1 (EVAL_099)

---

## 6. Key Qualitative Observations from Notes

1. **Boundary Refusal Handling**: On unsupported questions outside the 6-subject curriculum:
   - Stream A executed an explicit curriculum refusal on `EVAL_117` (Saga Pattern in Microservices).
   - Stream B executed an explicit curriculum refusal on `EVAL_099` (epoll I/O facility).
   - Both streams provided ungrounded technical responses to `EVAL_018` (Skip Lists), `EVAL_037` (Simplex), `EVAL_057` (BGP), and `EVAL_079` (Diffusion models).
2. **COCOMO Estimation (`EVAL_102`)**: Both streams exhibited hallucinated equations and false developer attributions (McCabe vs Dewey) rather than Barry Boehm's standard Basic COCOMO power formula $\text{Effort} = a \cdot (\text{KLOC})^b$.
3. **AVL Tree Worst-Case Search (`EVAL_001`)**: Stream A incorrectly asserted worst-case search complexity was $O(h)$ with a skewed tree and only average case is $O(\log n)$, whereas Stream B correctly identified $O(\log n)$ worst-case bound guaranteed by rotations.
4. **Circular Queue Indexing (`EVAL_005`)**: Stream B conflated a circular queue with a deque, incorrectly stating elements can be inserted and deleted from both ends.
