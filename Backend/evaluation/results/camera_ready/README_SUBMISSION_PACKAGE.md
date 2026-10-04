# EduGraphAI — Camera-Ready Research Manuscript & Final Submission Package

## 1. Project Title
**Evaluating Knowledge Graph-Grounded Retrieval-Augmented Generation in Higher Education: An Empirical Study of Answer Quality, Syllabus Boundaries, and Latency**

- **Project**: EduGraphAI — Knowledge Graph-Based Question Answering System for Educational Content
- **Author**: EduGraphAI Research Team
- **Date**: October 2026
- **Status**: Camera-Ready Submission Package (Part 11C Finalized)

---

## 2. Manuscript Files
This submission package contains the final publication-ready manuscript in three standard academic formats:

| Format | Filename | Description | File Size |
| :--- | :--- | :--- | :---: |
| **Markdown** | [`EDUGRAPHAI_CAMERA_READY_MANUSCRIPT.md`](file:///C:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/camera_ready/EDUGRAPHAI_CAMERA_READY_MANUSCRIPT.md) | Full 24-section manuscript formatted with GFM tables, math notation, and figure anchors | ~48.7 KB |
| **DOCX** | [`EDUGRAPHAI_CAMERA_READY_MANUSCRIPT.docx`](file:///C:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/camera_ready/EDUGRAPHAI_CAMERA_READY_MANUSCRIPT.docx) | Word document styled with academic typography, styled tables, embedded figures, and headings | ~1.67 MB |
| **PDF** | [`EDUGRAPHAI_CAMERA_READY_MANUSCRIPT.pdf`](file:///C:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/camera_ready/EDUGRAPHAI_CAMERA_READY_MANUSCRIPT.pdf) | Publication-ready 14-page PDF with running headers/footers ("Page X of Y"), wrapped table cells, and vector figures | ~1.88 MB |

---

## 3. Figures Included
Four publication-ready high-resolution figures are located in `Backend/evaluation/results/figures/` and embedded into the manuscript:

1. **Figure 1**: [`Figure_1_EduGraphAI_Architecture.png`](file:///C:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/figures/Figure_1_EduGraphAI_Architecture.png)
   *Title*: EduGraphAI System Architecture & Knowledge Graph Retrieval Workflow
   *Specification*: 5-tier architecture depicting Presentation Layer, FastAPI Gateway, Neo4j Graph Engine (**458 Concept Entities**, 497 Curriculum Edges), Dual-Mode Inference, and Educational Delivery.
2. **Figure 2**: [`Figure_2_Evaluation_Pipeline.png`](file:///C:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/figures/Figure_2_Evaluation_Pipeline.png)
   *Title*: Empirical Evaluation & Validation Methodology Pipeline
   *Specification*: 4-phase sequential workflow depicting Question Bank Construction ($N=120$), Local Benchmark Execution, Dual-Track Quality Evaluation (Automated LLM Judge + Blinded Human Audit $N=30$), and Statistical Validation with Holm-Bonferroni correction.
3. **Figure 3**: [`Figure_3_Human_Evaluation_Scores.png`](file:///C:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/figures/Figure_3_Human_Evaluation_Scores.png)
   *Title*: Human Double-Blind Quality Evaluation of KG-RAG vs. LLM-Only Baseline ($N=30$)
   *Specification*: Grouped bar chart with 95% percentile bootstrap confidence intervals ($B=10,000$, seed 42) across Correctness, Educational Relevance, Factual Grounding, and Unsupported Handling.
4. **Figure 4**: [`Figure_4_Local_Benchmark_Latency.png`](file:///C:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/figures/Figure_4_Local_Benchmark_Latency.png)
   *Title*: End-to-End Response Latency Comparison on Full Benchmark ($N=120$)
   *Specification*: Dual-panel figure depicting latency distributions (kernel density estimates and boxplots) and summary overhead metrics ($20.190\text{ s}$ vs. $47.294\text{ s}$, $2.34\times$ multiplier).

---

## 4. Dataset and Evaluation Artifacts
All underlying empirical data are preserved in the repository:
- **Evaluation Dataset**: `Backend/evaluation/eval_dataset.json` (120 curated questions across 6 subjects and 5 categories).
- **Execution Benchmark Output**: `Backend/evaluation/results/benchmark_results.json` (240 paired responses and raw latency logs).
- **Evaluation Rubric**: `Backend/evaluation/results/quality_evaluation_rubric.json` (Pre-registered scoring criteria).
- **Blinded Audit Mapping**: `Backend/evaluation/results/blind_mapping.json` (Cryptographic unblinding map).
- **Human Evaluation Template**: `Backend/evaluation/results/human_evaluation_template.csv` (Authoritative recorded human scores, $N=30$).
- **Automated Blind Evaluation**: `Backend/evaluation/results/automated_blind_quality_scores.csv` (Automated LLM judge scores).
- **Figure Source Data**: `Backend/evaluation/results/FIGURE_SOURCE_DATA.md` (Transcribed numbers verified against Part 9K).
- **Figure Descriptions**: `Backend/evaluation/results/PAPER_FIGURE_DESCRIPTIONS.md` (Formal figure specifications).
- **Audit Reports**: `Backend/evaluation/results/PART_11B_CONSISTENCY_AUDIT.md` and `PART_11B_DISCREPANCY_REPORT.md`.

---

## 5. Authoritative Statistical Source of Truth
The single authoritative statistical source of truth across the entire study is:
`Backend/evaluation/results/part_9k_validated_statistics.json`

### Confirmatory Findings Summary ($\alpha = 0.05$, Holm-Bonferroni Multiplicity Correction):
- **Correctness** ($n=30$): KG-RAG = $2.133$, LLM-Only = $2.600$, Difference = $-0.467$, $95\%$ Bootstrap CI $[-0.700, -0.233]$, Wilcoxon $W = 17.0$, raw $p = 0.00175$, Holm $p = 0.00875$. **Statistically Significant favoring Baseline**.
- **Educational Relevance** ($n=30$): KG-RAG = $2.167$, LLM-Only = $2.367$, Difference = $-0.200$, $95\%$ Bootstrap CI $[-0.433, +0.000]$, Wilcoxon $W = 9.0$, raw $p = 0.08326$, Holm $p = 0.24978$. **Not Statistically Significant**.
- **Factual Grounding** ($n=30$): KG-RAG = $2.167$, LLM-Only = $2.400$, Difference = $-0.233$, $95\%$ Bootstrap CI $[-0.400, -0.067]$, Wilcoxon $W = 5.0$, raw $p = 0.01963$, Holm $p = 0.07852$. **Not Significant After Multiplicity Correction** ($p > 0.05$).
- **Gold-Fact Coverage Rate** ($n=24$ supported queries, 60 reference facts): KG-RAG = $0.931$ (56/60, $93.3\%$), LLM-Only = $1.000$ (60/60, $100.0\%$), Difference = $-0.069$, $95\%$ Bootstrap CI $[-0.153, +0.000]$, Wilcoxon $W = 0.0$, raw $p = 0.10247$, Holm $p = 0.24978$. **Not Statistically Significant**.
- **Unsupported Handling** ($n=6$ out-of-scope queries): KG-RAG = $2.167$, LLM-Only = $1.333$, Difference = $+0.833$, $95\%$ Bootstrap CI $[+0.167, +1.500]$, Wilcoxon $W = 0.0$, raw $p = 0.25000$, Holm $p = 0.25000$. **Exploratory Directional Finding**.
- **Response Latency** ($N=120$ full benchmark): LLM-Only mean = $20.190\text{ s}$ ($SD = 11.150\text{ s}$, median $17.178\text{ s}$), KG-RAG mean = $47.294\text{ s}$ ($SD = 28.678\text{ s}$, median $38.962\text{ s}$), Overhead = $+27.104\text{ s}$ ($+134.2\%$, $2.34\times$ multiplier).

---

## 6. Model and Execution Environment Note
- **Evaluation Benchmark**: Executed locally using the Ollama runtime with `llama3.2:latest` (3-billion-parameter compact model, context window 4096 tokens, temperature 0.2, seed 42) on consumer hardware to guarantee local execution determinism and reproducibility.
- **Production Architecture**: Designed for cloud deployment utilizing the Groq API with `llama-3.3-70b-versatile` (70-billion-parameter frontier open model) connected to a live managed Neo4j AuraDB instance.
- **Critical Methodological Boundary**: The empirical benchmark directly evaluates the 3B local deployment under structured graph context; it does NOT directly evaluate the 70B cloud production deployment.

---

## 7. Known Experimental Limitations
1. **Model Capacity Discrepancy**: Performance characteristics of the compact 3B model under linear graph triples cannot be extrapolated to 70B frontier models without independent empirical testing.
2. **Absence of Document-RAG Baseline**: Due to the lack of a standardized multi-subject textbook passage corpus across all six disciplines, Document-RAG was not evaluated as an experimental baseline.
3. **Audit Sample Size**: While the benchmark includes 120 questions, the double-blind human audit evaluated 30 stratified items. Subgroup analyses on out-of-scope queries ($n=6$) are exploratory.
4. **Static Graph Store Fallback**: Offline benchmark execution utilized the deterministic static graph store fallback (`StaticGraphStore`) when cloud AuraDB was unavailable, providing an identical curriculum graph offline.

---

## 8. Exact Git Status Before Commit
The working directory contains the finalized Part 11C package and figure script updates. Production code (`Backend/app.py`, frontend, Neo4j configuration, authentication) has been left strictly untouched.

```text
 M Backend/evaluation/results/PAPER_FIGURE_DESCRIPTIONS.md
?? Backend/evaluation/generate_publication_figures.py
?? Backend/evaluation/results/FIGURE_SOURCE_DATA.md
?? Backend/evaluation/results/PART_11B_CONSISTENCY_AUDIT.md
?? Backend/evaluation/results/PART_11B_DISCREPANCY_REPORT.md
?? Backend/evaluation/results/camera_ready/
?? Backend/evaluation/results/figures/
?? data/data.zip
```

---

## 9. Recommended Next Git Action
Per Part 11C instructions, automated commits are strictly prohibited. The recommended Git command for the project maintainer is:

```powershell
git add Backend/evaluation/generate_publication_figures.py `
        Backend/evaluation/results/FIGURE_SOURCE_DATA.md `
        Backend/evaluation/results/PAPER_FIGURE_DESCRIPTIONS.md `
        Backend/evaluation/results/PART_11B_CONSISTENCY_AUDIT.md `
        Backend/evaluation/results/PART_11B_DISCREPANCY_REPORT.md `
        Backend/evaluation/results/figures/ `
        Backend/evaluation/results/camera_ready/

git commit -m "research: finalize camera-ready manuscript and submission package (Part 11C)"
```
