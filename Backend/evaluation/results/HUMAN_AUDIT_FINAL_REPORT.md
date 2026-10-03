# EduGraphAI — Human Blind Quality Evaluation Final Report

## 1. Executive Summary & Methodology
- **Evaluator**: Project Researcher / Human Domain Evaluator
- **Sample Size**: 30 questions (stratified sample: 6 subjects × 5 questions)
- **Evaluation Protocol**: Double-blind manual quality assessment.
- **Anonymity Guarantee**: Candidate Stream A and Candidate Stream B were presented anonymously in randomized order.
- **Rubric**: Standardized 0–3 scales across Correctness, Educational Relevance, Factual Grounding, Gold-Fact Semantic Coverage, and Unsupported Handling.
- **Data Source**: `Backend/evaluation/results/human_evaluation_template.csv`

---

## 2. Overall Anonymous Quality Results

| Metric | All Questions ($N=30$) | Supported Questions ($N=24$) | Unsupported Questions ($N=6$) |
| :--- | :---: | :---: | :---: |
| **Mean Correctness (0–3)** | Stream A: **2.433** \| Stream B: **2.3** | Stream A: **2.542** \| Stream B: **2.458** | Stream A: **2** \| Stream B: **1.667** |
| **Mean Relevance (0–3)** | Stream A: **2.367** \| Stream B: **2.167** | Stream A: **2.417** \| Stream B: **2.292** | Stream A: **2.167** \| Stream B: **1.667** |
| **Mean Grounding (0–3)** | Stream A: **2.333** \| Stream B: **2.233** | Stream A: **2.458** \| Stream B: **2.333** | Stream A: **1.833** \| Stream B: **1.833** |
| **Gold Fact Coverage** | Stream A: **60/60 (1.0)** \| Stream B: **56/60 (0.933)** | Same | N/A |
| **Unsupported Handling (0–3)** | Stream A: **1.833** \| Stream B: **1.667** | N/A | Same |

---

## 3. Subject-Level Anonymous Breakdown

| Subject | $N$ | Correctness A | Correctness B | Relevance A | Relevance B | Grounding A | Grounding B | Gold Coverage A | Gold Coverage B | Unsupported A | Unsupported B |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADA** | 5 | 2.8 | 2.2 | 2.4 | 2 | 3 | 2.4 | 1.0 | 1.0 | 3 | 2 |
| **CN** | 5 | 2.6 | 2.8 | 2.6 | 2.8 | 2.4 | 2.4 | 1.0 | 0.9 | 2 | 0 |
| **DSA** | 5 | 2.6 | 2.4 | 2.8 | 2.6 | 2.4 | 2.4 | 1.0 | 0.7 | 0 | 2 |
| **ML** | 5 | 2.6 | 2.6 | 2.6 | 2.2 | 2.6 | 2.8 | 1.0 | 1.0 | 0 | 0 |
| **OS** | 5 | 2.2 | 2 | 2 | 1.6 | 2 | 1.8 | 1.0 | 1.0 | 3 | 3 |
| **SEPM** | 5 | 1.8 | 1.8 | 1.8 | 1.8 | 1.6 | 1.6 | 1.0 | 1.0 | 3 | 3 |

---

## 4. Category-Level Anonymous Breakdown

| Category | $N$ | Correctness A | Correctness B | Relevance A | Relevance B | Grounding A | Grounding B | Gold Coverage A | Gold Coverage B |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **factual** | 6 | 2.667 | 2.667 | 2.333 | 2.333 | 2.667 | 2.667 | 1.0 | 1.0 |
| **conceptual** | 6 | 2.333 | 2.833 | 2.833 | 2.667 | 2.5 | 2.667 | 1.0 | 1.0 |
| **comparison** | 6 | 2.833 | 2.5 | 2.333 | 2 | 2.5 | 2.167 | 1.0 | 0.833 |
| **relationship** | 6 | 2.333 | 1.833 | 2.167 | 2.167 | 2.167 | 1.833 | 1.0 | 0.889 |
| **unsupported** | 6 | 2 | 1.667 | 2.167 | 1.667 | 1.833 | 1.833 | N/A | N/A |

---

## 5. Audit Integrity & Blinding Lock
- The human evaluation scores were locked before unblinding.
- Stream A and Stream B remained blinded throughout data collection and descriptive statistical calculations.
- No system names (`llm_only`, `kg_rag`) were used to bias scores.
