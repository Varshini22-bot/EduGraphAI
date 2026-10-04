# Publication-Ready Figure Descriptions: EduGraphAI Evaluation Study

This document specifies the four primary figures designed for the EduGraphAI research manuscript, grounded directly in the measured evaluation dataset and verified architecture.

---

### Figure 1: EduGraphAI End-to-End System Architecture

- **Figure Title**: End-to-End System Architecture of EduGraphAI
- **Purpose**: Illustrates the operational decomposition between client presentation, API routing, asynchronous graph services, persistent databases, and language model inference backends.
- **Visual Structure**: Multi-tier architectural block diagram showing four interconnected layers:
  1. **Client Tier**: Next.js 14 / React frontend with interactive graph visualization canvas (`vis-network`), responsive markdown rendering, follow-up pedagogical action pills, and authenticated user profile views.
  2. **API & Service Tier**: FastAPI application gateway exposing REST endpoints (`/api/query`, `/api/ask`, `/api/auth`, `/api/graph`), coordinating conversation history management, and orchestrating the RAG execution service.
  3. **Data & Retrieval Tier**: Neo4j Graph Database (managed Neo4j AuraDB with local fallback failover) storing 458 curriculum concept nodes (497 edges across 6 subjects), hierarchical taxonomy (`IS_A`, `PART_OF`), and prerequisite relations (`USES`, `REQUIRES`), alongside SQLite / SQLAlchemy for relational student accounts and shared conversations.
  4. **Inference Tier**: Dual-mode LLM backend supporting Groq Cloud API (`llama-3.3-70b-versatile`) in production and local Ollama daemon (`llama3.2:latest`, context 4096 tokens) in local/evaluation environments.
- **Interpretation**: Demonstrates how EduGraphAI decouples curriculum graph traversal from generative language modeling, enabling modular retrieval failover and flexible deployment across cloud and local runtimes.

---

### Figure 2: Empirical Evaluation & Validation Methodology Pipeline

- **Figure Title**: Empirical Evaluation & Validation Methodology Pipeline
- **Purpose**: Illustrates the end-to-end experimental workflow from multi-subject query bank construction through local paired execution, dual-track quality evaluation, and rigorous statistical validation.
- **Visual Structure**: Four-stage sequential methodology diagram:
  1. **Stage 1: Question Bank Construction ($N=120$)**: 6 undergraduate computer science subjects (ADA, CN, DSA, ML, OS, SEPM) $\times$ 20 questions across 5 pedagogical categories (Factual, Conceptual, Comparison, Relationship, Unsupported Boundary).
  2. **Stage 2: Local Benchmark Execution**: Paired execution on local Ollama runtime (`llama3.2:latest`, 3B) under deterministic settings (temperature 0.2, seed 42) comparing KG-RAG against unaugmented LLM-only generation, with end-to-end latency measurement across all 240 runs.
  3. **Stage 3: Dual-Track Quality Evaluation**:
     - *Automated Track*: LLM-as-a-judge scoring across the full benchmark ($N=120$) using a 0–3 evaluation rubric.
     - *Blinded Human Audit Track*: Rigorous double-blind evaluation of a stratified representative sample ($N=30$, 5 per subject, 24 supported, 6 unsupported), with system identity masked (Answer A vs. Answer B) and independent scoring against gold facts.
  4. **Stage 4: Statistical Validation & Multiplicity Correction**: Formal confirmatory hypothesis testing via Wilcoxon signed-rank tests ($W$), family-wise error rate control via Holm-Bonferroni step-down correction across 5 primary outcomes ($\alpha=0.05$), and non-parametric percentile bootstrap 95% confidence intervals ($B=10,000$ resamples, seed 42).
- **Interpretation**: Highlights the methodological rigor, blinding integrity, and multiple-comparison correction employed to prevent false-positive discovery in LLM educational benchmarking.

---

### Figure 3: Human Evaluation Comparison Across Quality Dimensions

- **Figure Title**: Human Double-Blind Quality Evaluation of KG-RAG vs. LLM-Only Baseline ($N=30$)
- **Purpose**: Displays the comparative performance of EduGraphAI KG-RAG and the LLM-only baseline across primary and secondary quality dimensions evaluated in the double-blind human audit.
- **Plot Type**: Grouped bar chart with error bars representing 95% percentile bootstrap confidence intervals.
- **Axes**:
  - **X-axis**: Evaluated Quality Dimensions:
    - *Correctness* ($n=30$)
    - *Educational Relevance* ($n=30$)
    - *Factual Grounding* ($n=30$)
    - *Unsupported Handling* ($n=6$)
  - **Y-axis**: Mean Evaluation Score on a 0–3 Ordinal Scale ($0 = \text{Poor/Fails}$, $1 = \text{Marginal}$, $2 = \text{Good}$, $3 = \text{Excellent}$).
- **Data Series**:
  - Series 1: **EduGraphAI KG-RAG** (Correctness: $2.133 \pm 0.20$; Relevance: $2.167 \pm 0.20$; Grounding: $2.167 \pm 0.17$; Unsupported Handling: $2.167 \pm 0.65$).
  - Series 2: **LLM-Only Baseline** (Correctness: $2.600 \pm 0.20$; Relevance: $2.367 \pm 0.20$; Grounding: $2.400 \pm 0.20$; Unsupported Handling: $1.333 \pm 0.80$).
- **Sample Size**: $N=30$ paired items for primary metrics; $n=6$ items for unsupported handling. Derived from [`figure_data.csv`](file:///c:/Users/varsh/OneDrive/Attachments/Desktop/Knowledge_Graph_Project/Backend/evaluation/results/figure_data.csv).
- **Statistical Annotations**:
  - Correctness: Statistically significant ($p < 0.01$ after Holm-Bonferroni correction, favoring Baseline).
  - Relevance: Not statistically significant ($p = 0.25$).
  - Grounding: Not statistically significant after Holm-Bonferroni correction ($p = 0.079$).
  - Unsupported Handling: Exploratory finding ($p = 0.25$, $n=6$).
- **Interpretation**: Directly demonstrates the empirical nuance: the unaugmented baseline achieved higher correctness scores on supported queries, while KG-RAG exhibited directional exploratory utility in curriculum boundary guardrails.

---

### Figure 4: End-to-End Response Latency Comparison ($N=120$)

- **Figure Title**: Response Generation Latency Distribution Across 120 Benchmark Questions
- **Purpose**: Quantifies the computational latency cost incurred by multi-hop graph retrieval compared to direct unaugmented generation.
- **Plot Type**: Paired distribution plot (Kernel Density Estimation and overlaid Box-and-Whisker plots).
- **Axes**:
  - **X-axis**: System Architecture (LLM-Only Baseline vs. EduGraphAI KG-RAG).
  - **Y-axis**: End-to-End Latency in seconds (scale 0 to 100 seconds).
- **Data Series**:
  - **LLM-Only Baseline**: Mean = $20.190\text{ s}$, $SD = 7.152\text{ s}$, Median = $19.34\text{ s}$, $\text{IQR} = [14.6\text{ s}, 23.0\text{ s}]$, Range = $[8.2\text{ s}, 38.4\text{ s}]$.
  - **EduGraphAI KG-RAG**: Mean = $47.294\text{ s}$, $SD = 15.654\text{ s}$, Median = $44.18\text{ s}$, $\text{IQR} = [35.2\text{ s}, 54.1\text{ s}]$, Range = $[21.8\text{ s}, 89.6\text{ s}]$.
- **Sample Size**: Full benchmark of $N=120$ paired questions executed under identical local conditions (`llama3.2:latest`, Ollama runtime, 4096 context tokens).
- **Annotation**: Mean difference = $+27.104\text{ s}$ ($2.34\times$ latency multiplier).
- **Interpretation**: Clearly highlights the significant latency penalty of graph-augmented generation on local hardware, isolating the operational trade-off that educational deployments must weigh against curriculum grounding requirements.
