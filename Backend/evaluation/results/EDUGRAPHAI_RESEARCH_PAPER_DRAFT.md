# Evaluating Knowledge Graph-Grounded Retrieval-Augmented Generation in Higher Education: An Empirical Study of Answer Quality, Syllabus Boundaries, and Latency

## Abstract
Large Language Models (LLMs) are widely used in educational question answering, yet unconstrained generation risks introducing ungrounded claims or straying beyond course syllabi. Knowledge Graph Retrieval-Augmented Generation (KG-RAG) offers structured concept traversal and explicit syllabus grounding, but its empirical impact on educational quality remains insufficiently tested. We present EduGraphAI, an educational QA architecture coupling a Neo4j knowledge graph of computer science curricula with language model synthesis. We evaluate KG-RAG against an unaugmented baseline across a 120-question benchmark spanning six disciplines and five question categories. Generation quality was assessed via a double-blind, paired human audit ($N=30$) using pre-registered rubrics and analyzed with two-sided Wilcoxon signed-rank tests under Holm-Bonferroni correction ($\alpha = 0.05$). The human audit revealed a statistically significant difference in correctness favoring the unaugmented baseline ($2.600$ vs. $2.133$, $p = 0.0088$), reflecting greater fluency and elaboration in unconstrained small local models (`llama3.2`). Educational relevance ($p = 0.2498$) and factual grounding ($p = 0.0785$) showed no significant differences after correction, while both systems achieved high gold-fact coverage ($93.3\%$ vs. $100.0\%$). On out-of-scope queries ($n=6$), KG-RAG demonstrated an exploratory directional advantage in syllabus boundary redirection ($+0.833$ points), though limited sample size precluded statistical significance ($p = 0.2500$). Graph retrieval also incurred a $2.34\times$ latency penalty ($47.29\text{ s}$ vs. $20.19\text{ s}$, $N=120$). This study demonstrates that graph grounding does not automatically improve perceived answer quality, highlighting essential trade-offs among model capacity, retrieval noise, and latency.

## Keywords
Educational Question Answering, Knowledge Graph, Retrieval-Augmented Generation, Syllabus Grounding, Double-Blind Evaluation, Statistical Multiplicity Correction, Educational Technology

---

## 1. Introduction
The integration of generative Large Language Models (LLMs) into digital learning platforms has transformed computer-assisted education, enabling automated tutoring, on-demand problem solving, and personalized instructional dialogue. However, deploying general-purpose foundation models in educational contexts exposes critical pedagogical challenges. Foundation models trained on uncurated corpora frequently produce fluent yet factually inaccurate assertions, hallucinate non-existent technical specifications, or introduce advanced material that exceeds undergraduate curricular boundaries. For university students preparing for structured examinations, receiving plausible but ungrounded explanations can reinforce misconceptions and undermine academic achievement.

To address factual drift, Retrieval-Augmented Generation (RAG) has emerged as a prominent paradigm, conventionally supplying relevant document passages retrieved via vector similarity search into the prompt context. While effective in open-domain tasks, unstructured passage retrieval often struggles with hierarchical pedagogical knowledge, prerequisite dependencies, and precise curriculum boundaries. In contrast, Knowledge Graphs (KGs) represent domain knowledge as structured entities connected by explicit, semantically typed relationships (such as taxonomic hierarchies and prerequisite pathways). Augmenting language generation with Knowledge Graph retrieval (KG-RAG) offers the potential to bound educational dialogue to verified syllabus concepts, provide structured learning trajectories, and reject out-of-scope queries.

Nevertheless, Knowledge Graph augmentation introduces distinct architectural complexities. Graph entity extraction can misidentify ambiguous technical terms, multi-hop Cypher queries incur database latency, and static graph contexts can constrain generative fluency. Despite widespread enthusiasm for graph-grounded AI, empirical research examining whether KG-RAG measurably improves human-judged educational answer quality compared to unaugmented baselines remains limited.

In this paper, we present an empirical evaluation of **EduGraphAI**, an open-source educational learning assistant that couples a Neo4j knowledge graph representing undergraduate computer science curricula with language model synthesis. Through a standardized 120-question multi-subject benchmark and a double-blind, paired human audit ($N=30$) with rigorous Holm-Bonferroni multiplicity correction, we evaluate whether graph grounding enhances answer correctness, relevance, factual grounding, and syllabus boundary adherence, while quantifying the associated latency overhead.

---

## 2. Problem Statement
In higher education environments, an AI learning assistant must satisfy multi-faceted pedagogical criteria:
1. **Curricular Relevance**: Responses must adhere strictly to the target course syllabus rather than providing open-ended web commentary.
2. **Factual Grounding**: Assertions must be anchored in verified academic facts and formal definitions.
3. **Conceptual Coherence**: Explanations must clarify structural relationships (e.g., taxonomies, tradeoffs, and prerequisite sequences).
4. **Curriculum Guardrails**: The assistant must identify out-of-scope questions and redirect students rather than fabricating plausible answers for unstudied material.
5. **Operational Responsiveness**: Interactive learning requires low response latency suitable for conversational engagement.

Balancing factual grounding and syllabus guardrails against generation fluency and system latency constitutes a fundamental engineering trade-off.

---

## 3. Research Questions
This study investigates the following primary research question:
> **RQ**: How does Knowledge Graph-grounded Retrieval-Augmented Generation affect the quality, factual grounding, syllabus-boundary behavior, and latency of educational question answering compared with an unaugmented LLM-only baseline?

This overarching inquiry decomposes into four specific sub-questions:
- **RQ1 (Answer Quality)**: Does graph retrieval improve the subjective correctness, educational relevance, and factual grounding of answers on supported curriculum questions as judged by domain evaluators?
- **RQ2 (Factual Coverage)**: Does KG-RAG achieve comparable or higher coverage of reference syllabus facts compared to unaugmented generation?
- **RQ3 (Syllabus Boundary Adherence)**: Does knowledge graph grounding assist the model in recognizing out-of-scope curriculum questions and executing appropriate refusals?
- **RQ4 (Latency Trade-Off)**: What computational latency overhead is introduced by multi-hop graph retrieval relative to direct generation?

---

## 4. Contributions
This paper provides the following research contributions:
1. **Architectural Implementation**: A complete, functioning educational architecture integrating Neo4j graph traversal with FastAPI and Next.js, supporting hierarchical curriculum navigation, interactive graph visualization, and examination-calibrated generation.
2. **Standardized Evaluation Benchmark**: A curated 120-question evaluation dataset spanning six computer science subjects (ADA, CN, DSA, ML, OS, and SEPM) across five pedagogical question categories (factual, conceptual, comparison, relationship, and out-of-scope).
3. **Double-Blind Evaluation Protocol**: A rigorous, double-blind human audit methodology ($N=30$ paired observations) with pre-registered scoring rubrics and unblinding validation to prevent confirmation bias.
4. **Multiplicity-Corrected Statistical Treatise**: Statistical analysis employing paired two-sided Wilcoxon signed-rank tests with Holm-Bonferroni family-wise error control, percentile bootstrap confidence intervals ($B=10,000$), and Cohen's $d_z$ effect sizes.
5. **Empirical Trade-Off Analysis**: Transparent documentation demonstrating that graph grounding did not improve human-judged correctness over the baseline on small local models, incurred a $2.34\times$ latency penalty, but exhibited exploratory directional utility in syllabus boundary enforcement.

---

## 5. Related Work

### 5.1 Retrieval-Augmented Generation (RAG)
Retrieval-Augmented Generation combines parametric language model weights with non-parametric external retrieval to reduce hallucinations and ground responses in authoritative documents. Standard RAG frameworks divide text into dense vector embeddings indexed in vector databases. However, vector similarity search operates on surface semantic proximity, frequently retrieving disconnected passage fragments that fail to capture multi-hop relational dependencies or structured taxonomies.

### 5.2 Knowledge Graphs in Education
Knowledge Graphs represent domain concepts as nodes and educational relationships as directed edges (e.g., `PREREQUISITE_OF`, `PART_OF`, `USES`). In educational technology, ontologies have supported curriculum modeling, automated learning path recommendation, and adaptive assessment generation. Integrating KGs with generative LLMs (KG-RAG) has been proposed to inject structured relational context into generation prompts, enabling systems to ground explanations in formal subject topologies.

### 5.3 Hallucination and Boundary Enforcement in Educational QA
Educational question answering requires distinct guardrails compared to open-domain search. While open-domain systems prioritize answering every query comprehensively, educational systems must recognize curriculum limits. An ungrounded model that invents syllabus-aligned explanations for concepts outside the examination scope misleads students regarding exam preparation. Prior research highlights the difficulty foundation models face in knowing what they do not know, motivating structural graph-boundary constraints.

---

## 6. Existing System
Conventional educational chatbots typically rely on unaugmented foundation models accessed via cloud APIs. In this configuration, an incoming student query is forwarded directly into the prompt context with system instructions requesting academic tone and mark-appropriate length. While this approach offers rapid execution latency and fluent linguistic delivery, it lacks external grounding against a defined syllabus. The model relies entirely on pretraining weights, resulting in vulnerability to factual hallucination, an inability to verify whether a topic is within the curriculum, and absence of visual conceptual structures for learners.

---

## 7. Proposed EduGraphAI System

### 7.1 System Architecture
EduGraphAI is engineered as a multi-tier educational platform:
- **Presentation Layer**: Built with Next.js 14 and Tailwind CSS, featuring a responsive chat interface, interactive node-link graph visualization powered by `vis-network`, dynamic markdown math rendering, and follow-up pedagogical action chips (e.g., "explain simply", "show prerequisites", "exam viva questions").
- **Application Services Layer**: Implemented in FastAPI (Python 3.14), providing asynchronous REST API routing (`/api/query`, `/api/ask`, `/api/auth`, `/api/graph`), session orchestration, and coordination of the RAG pipeline.
- **Data & Storage Layer**: Neo4j Graph Database (managed Neo4j AuraDB with automated local failover fallback) storing curriculum entities and relational edges, alongside SQLite / SQLAlchemy for student account management and conversation persistence.
- **Inference Layer**: Dual-mode LLM integration supporting Groq Cloud API (`llama-3.3-70b-versatile`) in production and local Ollama daemon (`llama3.2:latest`, context 4096 tokens) in offline evaluation environments.

### 7.2 Knowledge Graph Construction
The EduGraphAI knowledge base models undergraduate computer science curricula across six foundational courses:
- **ADA**: Analysis & Design of Algorithms
- **CN**: Computer Networks
- **DSA**: Data Structures & Algorithms
- **ML**: Machine Learning
- **OS**: Operating Systems
- **SEPM**: Software Engineering & Project Management

Each subject ontology contains canonical `Concept` nodes enriched with properties (`name`, `subject`, `definition`, `importance`, `marks_weight`). Nodes are interconnected via typed edges:
- `IS_A`: Taxonomic classification (e.g., `AVL Tree` $\xrightarrow{\text{IS\_A}}$ `Binary Search Tree`)
- `PART_OF`: Compositional decomposition (e.g., `Transport Layer` $\xrightarrow{\text{PART\_OF}}$ `OSI Model`)
- `USES` / `REQUIRES`: Prerequisite dependencies forming learning pathways (e.g., `Dijkstra's Algorithm` $\xrightarrow{\text{USES}}$ `Priority Queue`)
- `COMPARED_WITH`: Direct analytical contrasts (e.g., `TCP` $\xrightarrow{\text{COMPARED\_WITH}}$ `UDP`)

### 7.3 Retrieval Pipeline
The retrieval pipeline executes sequentially:
1. **Query Processing**: Incoming query text is parsed for canonical topic mentions, context topics from prior conversational turns, and target examination mark allocations (2, 5, or 10 marks).
2. **Topic Extraction**: `TopicExtractor` employs token normalization and regex pattern matching against graph entities.
3. **Graph Traversal**: Parameterized Cypher queries retrieve:
   - The canonical concept node definition and metadata.
   - Outgoing and incoming 1-hop and 2-hop relational neighbors.
   - Prerequisite chains resolved via `USES` edges.
   - Pedagogical recommendations via graph centrality.
4. **Curriculum Guardrail Routing**: If the identified concept does not map to a recognized syllabus node, the system flags the query as out-of-scope.

### 7.4 Question Processing
The system detects contextual follow-up directives through pattern matching (e.g., "Binary Search — give a more detailed explanation, for 8 marks"), enabling students to dynamically steer explanation depth while retaining graph context.

### 7.5 Answer Generation
`PromptBuilder` structures retrieved graph triples into an examination-calibrated prompt:
```text
System: You are an expert Computer Science Professor and Examiner.
Syllabus Knowledge Base Grounding:
- Topic: [Target Concept]
- Definition: [Graph Property Definition]
- Relational Context: [Connected Nodes and Edges]
- Prerequisite Path: [Prerequisite Sequence]
Instruction: Answer the following examination question strictly using the verified
syllabus facts provided. If the question asks for topics not in the syllabus, politely refuse.
Question: [Student Query] (Target: [Marks] Marks)
```
The prompt is dispatched to the LLM backend for synthesis.

### 7.6 Educational Chat Interface
Upon receiving the synthesized answer, the frontend renders the markdown text alongside an interactive interactive subgraph showing the active topic and its immediate neighbors, prerequisite learning paths, and clickable recommendation chips.

---

## 8. Experimental Methodology

### 8.1 Research Design
We conducted an empirical within-subjects evaluation comparing **EduGraphAI KG-RAG** against an **unaugmented LLM-Only Baseline**. Both systems operated on identical hardware using the local Ollama runtime hosting `llama3.2:latest` (3B parameters, `OLLAMA_NUM_CTX=4096`).

### 8.2 Dataset
The benchmark comprises 120 curated computer science examination questions (`Backend/evaluation/eval_dataset.json`), developed to mirror standard university examination papers.

### 8.3 Subjects
The 120 questions are distributed uniformly across six academic subjects:
- ADA ($n=20$)
- CN ($n=20$)
- DSA ($n=20$)
- ML ($n=20$)
- OS ($n=20$)
- SEPM ($n=20$)

### 8.4 Question Categories
Within each subject, questions are stratified across five distinct pedagogical categories (4 questions per category per subject):
- **Factual (2 marks)**: Direct definitions, asymptotic bounds, and standard principles ($n=24$, supported).
- **Conceptual (5 marks)**: Mechanistic explanations and working principles ($n=24$, supported).
- **Comparison (5/10 marks)**: Structured analytical differences between related concepts ($n=24$, supported).
- **Relationship (5/10 marks)**: Multi-hop interactions, dependency chains, and architectural hierarchies ($n=24$, supported).
- **Unsupported (0 marks)**: Technical computer science questions intentionally selected from topics outside the defined course syllabus to test guardrails ($n=24$, out-of-scope).

Across the full benchmark, 96 questions represent supported curriculum concepts, and 24 represent unsupported out-of-scope concepts.

### 8.5 Baselines
- **LLM-Only Baseline**: The base language model (`llama3.2:latest`) receives the question and examination mark instruction directly without graph retrieval or external context.
- **EduGraphAI KG-RAG**: The model receives the question embedded within the structured graph context retrieved from Neo4j via `GraphService`.

### 8.6 Evaluation Metrics
Quality evaluation utilized five validated metrics:
1. **Correctness (0–3 scale)**: Technical accuracy, absence of erroneous claims, and alignment with academic computer science facts.
2. **Educational Relevance (0–3 scale)**: Pedagogical clarity, suitability for university examination preparation, and target mark calibration.
3. **Factual Grounding (0–3 scale)**: Degree to which statements are verifiably anchored in recognized syllabus facts without extraneous ungrounded assertions.
4. **Gold-Fact Coverage Rate (0.0–1.0 rate)**: Proportion of pre-defined reference ground-truth facts semantically covered in the answer (evaluated on supported questions, $n=24$, 60 total reference facts).
5. **Unsupported Handling (0–3 scale)**: Appropriateness in recognizing curriculum boundaries, refusing out-of-scope technical queries, and redirecting students ($0 = \text{Answers as syllabus topic}$, $3 = \text{Clear refusal and syllabus redirection}$).

### 8.7 Human Evaluation
To obtain ground-truth validation free from automated evaluation bias, a domain researcher conducted a double-blind audit on a stratified 30-question sample (5 questions per subject: 4 supported, 1 unsupported; 24 supported, 6 unsupported). Candidate answers were presented in randomized order labeled strictly as "Answer A" and "Answer B". System identities were blinded via cryptographic hashes in `blind_mapping.json`. Scores were recorded manually in `human_evaluation_template.csv` before unblinding.

### 8.8 Statistical Analysis
All statistical tests were executed using SciPy 1.18.1 and statsmodels 0.15.0:
- **Hypothesis Testing**: Two-sided paired Wilcoxon signed-rank tests with zero-difference pruning (`zero_method='wilcox'`).
- **Multiple-Comparison Adjustment**: Holm-Bonferroni step-down correction applied across the family of five evaluated outcome metrics at $\alpha = 0.05$:
  $$p_{(i)}^{\text{Holm}} = \min\left(1, \max_{k \le i} ((m - k + 1) \cdot p_{(k)})\right)$$
- **Confidence Intervals**: 95% percentile bootstrap confidence intervals estimated over $B=10,000$ paired resamples (seed 42).
- **Effect Sizes**: Paired Cohen's $d_z = \bar{d} / SD_d$ with sample degrees of freedom ($ddof=1$).

### 8.9 Latency Evaluation
Response latency was logged across all 120 benchmark questions, recording end-to-end execution duration from request submission to completed token generation. Latency analysis is kept strictly separate from human quality ratings.

---

## 9. Results

### 9.1 Human Evaluation
Table 1 summarizes the validated paired statistical findings from the double-blind human audit.

#### Table 1: Validated Statistical Comparison of EduGraphAI KG-RAG vs. LLM-Only Baseline ($N=30$)
| Metric | Sample ($n$) | KG-RAG Mean | LLM-Only Mean | Mean Diff ($d$) | Median Diff | 95% Bootstrap CI | Wilcoxon $W$ | Raw $p$ | Holm Adjusted $p$ | Effect Size ($d_z$) | Validated Conclusion ($\alpha = 0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Correctness** | 30 | 2.133 | 2.600 | $-0.467$ | $-0.500$ | $[-0.700, -0.233]$ | 17.0 | $0.00175$ | **$0.00875$** | $-0.685$ | **Statistically Significant** ($p < 0.01$, favors Baseline) |
| **Educational Relevance** | 30 | 2.167 | 2.367 | $-0.200$ | $0.000$ | $[-0.433, +0.000]$ | 9.0 | $0.08326$ | $0.24978$ | $-0.328$ | Not Significant ($p = 0.25$) |
| **Factual Grounding** | 30 | 2.167 | 2.400 | $-0.233$ | $0.000$ | $[-0.400, -0.067]$ | 5.0 | $0.01963$ | $0.07852$ | $-0.463$ | **Not Significant After Holm Correction** ($p > 0.05$) |
| **Gold-Fact Coverage Rate** | 24 | 0.931 | 1.000 | $-0.069$ | $0.000$ | $[-0.153, +0.000]$ | 0.0 | $0.10247$ | $0.24978$ | $-0.366$ | Not Significant ($p = 0.25$) |
| **Unsupported Handling** | 6 | 2.167 | 1.333 | $+0.833$ | $+0.500$ | $[+0.167, +1.500]$ | 0.0 | $0.25000$ | $0.25000$ | $+0.848$ | **Exploratory Finding** (Not Significant, $p = 0.25$) |

*Notes: Differences calculated as $\text{KG-RAG} - \text{LLM-Only}$. Raw $p$-values computed via SciPy `scipy.stats.wilcoxon`. Multiplicity adjustment via Holm-Bonferroni across all 5 outcome tests.*

### 9.2 Statistical Significance

#### Correctness
On the primary metric of Correctness, the LLM-only baseline achieved a higher mean rating than KG-RAG ($2.600$ vs. $2.133$; paired mean difference $d = -0.467$, $95\%\text{ CI } [-0.700, -0.233]$, Wilcoxon $W = 17.0$, raw $p = 0.00175$, Holm-adjusted $p = 0.00875$, $d_z = -0.685$). This difference remained statistically significant after multiple-comparison correction ($p < 0.01$). In this sample, the base 3B model generated more expansive, fluent explanations when unprompted with external context, whereas KG-RAG responses were more concise and incorporated conservative refusals on out-of-scope items.

#### Educational Relevance
Educational Relevance scores were comparable between systems ($2.167$ for KG-RAG vs. $2.367$ for Baseline; paired mean difference $d = -0.200$, Wilcoxon $W = 9.0$, raw $p = 0.08326$, Holm-adjusted $p = 0.24978$). No statistically significant difference was detected. Both systems produced responses aligned with university examination conventions.

#### Factual Grounding
While the raw unadjusted test indicated a descriptive divergence favoring the baseline ($2.400$ vs. $2.167$, raw $p = 0.01963$), **this difference was not statistically significant following Holm-Bonferroni correction** (Holm-adjusted $p = 0.07852 > 0.05$; $95\%\text{ CI } [-0.400, -0.067]$). Under family-wise error control, the evidence is insufficient to reject the null hypothesis of equal factual grounding.

### 9.3 Gold-Fact Coverage
Across the 24 supported curriculum queries evaluated in the human audit (encompassing 60 total reference gold facts):
- **Aggregate Fact Coverage**: KG-RAG covered 56 of 60 reference facts ($93.3\%$), while the LLM-only baseline covered 60 of 60 reference facts ($100.0\%$).
- **Question-Level Mean Rate**: KG-RAG achieved a mean question coverage rate of $0.9306$ (median $1.0000$), compared to $1.0000$ (median $1.0000$) for the baseline.
- **Statistical Inference**: The paired difference in question-level coverage rate was not statistically significant (Wilcoxon $W = 0.0$, raw $p = 0.10247$, Holm-adjusted $p = 0.24978$, $95\%\text{ CI } [-0.153, +0.000]$). Both systems achieved near-ceiling factual retrieval on core syllabus topics.

### 9.4 Unsupported Questions
For the 6 out-of-scope curriculum questions:
- KG-RAG achieved a higher mean rating in curriculum boundary enforcement ($2.167$ vs. $1.333$; paired mean difference $d = +0.833$, Cohen's $d_z = +0.848$, $95\%\text{ CI } [+0.167, +1.500]$).
- While the unaugmented baseline routinely provided detailed technical answers treating out-of-scope queries as syllabus concepts, KG-RAG successfully recognized graph absence and delivered refusal/redirection notices.
- However, because only $N_r = 3$ non-zero paired differences existed in this small subset, the non-parametric Wilcoxon test yielded $p = 0.25000$ (Holm-adjusted $p = 0.25000$). Consequently, this finding is classified as an **exploratory descriptive finding**; the bootstrap confidence interval excludes zero descriptively but cannot substitute for confirmatory hypothesis testing.

### 9.5 Subject-Level Results
Table 2 presents descriptive metrics across academic subjects ($n=5$ per subject in the human audit).

#### Table 2: Subject-Level Descriptive Breakdown
| Subject | Sample ($n$) | KG-RAG Correctness | LLM-Only Correctness | KG-RAG Relevance | LLM-Only Relevance | KG-RAG Grounding | LLM-Only Grounding | KG-RAG Facts Covered | Baseline Facts Covered | Total Facts |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADA** | 5 | 2.20 | 2.80 | 2.20 | 2.20 | 2.40 | 3.00 | 10 / 10 | 10 / 10 | 10 |
| **CN** | 5 | 2.40 | 3.00 | 2.40 | 3.00 | 2.20 | 2.60 | 9 / 10 | 10 / 10 | 10 |
| **DSA** | 5 | 2.40 | 2.60 | 2.60 | 2.80 | 2.40 | 2.40 | 7 / 10 | 10 / 10 | 10 |
| **ML** | 5 | 2.60 | 2.60 | 2.40 | 2.40 | 2.60 | 2.80 | 10 / 10 | 10 / 10 | 10 |
| **OS** | 5 | 1.60 | 2.60 | 1.60 | 2.00 | 1.80 | 2.00 | 10 / 10 | 10 / 10 | 10 |
| **SEPM** | 5 | 1.60 | 2.00 | 1.80 | 1.80 | 1.60 | 1.60 | 10 / 10 | 10 / 10 | 10 |

Across subjects, Machine Learning (ML) exhibited the highest performance parity between systems ($2.60$ for both), while Operating Systems (OS) and Software Engineering (SEPM) showed larger descriptive gaps favoring the baseline, largely driven by strict graph refusals on out-of-scope systems topics.

### 9.6 Category-Level Results
Table 3 details performance across pedagogical categories ($n=6$ per category).

#### Table 3: Category-Level Descriptive Breakdown
| Category | Sample ($n$) | KG-RAG Correctness | Baseline Correctness | Diff Correctness | KG-RAG Relevance | Baseline Relevance | Diff Relevance | KG-RAG Grounding | Baseline Grounding | Diff Grounding |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Factual** | 6 | 2.667 | 2.667 | $+0.000$ | 2.333 | 2.333 | $+0.000$ | 2.667 | 2.667 | $+0.000$ |
| **Conceptual** | 6 | 2.500 | 2.667 | $-0.167$ | 2.833 | 2.667 | $+0.167$ | 2.500 | 2.667 | $-0.167$ |
| **Comparison** | 6 | 2.333 | 3.000 | $-0.667$ | 2.000 | 2.333 | $-0.333$ | 2.167 | 2.500 | $-0.333$ |
| **Relationship** | 6 | 1.667 | 2.500 | $-0.833$ | 2.000 | 2.333 | $-0.333$ | 1.833 | 2.167 | $-0.333$ |
| **Unsupported** | 6 | 1.500 | 2.167 | $-0.667$ | 1.667 | 2.167 | $-0.500$ | 1.667 | 2.000 | $-0.333$ |

On basic factual queries, both systems performed identically ($2.667$). Differences favoring the baseline emerged predominantly on multi-hop comparison and relationship questions, where the baseline's unconstrained elaboration received higher subjective evaluator scores than the concise graph summaries.

### 9.7 Latency
Table 4 displays latency metrics across all 120 benchmark queries.

#### Table 4: Latency Comparison on Full Benchmark ($N=120$)
| Architecture | Sample ($N$) | Mean Latency | Standard Deviation ($SD$) | Median Latency | Multiplier |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LLM-Only Baseline** | 120 | 20.190 s | 7.152 s | 19.340 s | $1.00\times$ |
| **EduGraphAI KG-RAG** | 120 | 47.294 s | 15.654 s | 44.180 s | **$2.34\times$** |

Knowledge graph augmentation incurred a statistically significant latency overhead of $+27.104\text{ s}$ per query. This $2.34\times$ slowdown reflects the dual-stage execution cost: Phase 1 executes entity parsing, Cypher query compilation, and multi-hop neighbor retrieval against Neo4j; Phase 2 performs prompt formatting and extended LLM context processing.

### 9.8 Automated vs Human Evaluation
Comparison between the human audit and an automated LLM judge (`phi4-mini:latest` via Ollama) on the 30 audit pairs ($N=60$ individual answers) revealed substantial disagreement:
- **Exact Agreement Rates**: Correctness: **55.0%**, Educational Relevance: **38.3%**, Factual Grounding: **43.3%**.
- **Systematic Bias**: The automated judge exhibited pronounced leniency bias, rating candidate answers $0.38$ to $0.65$ points higher on average than the human evaluator.
- **Pedagogical Evaluation Divergence**: The automated evaluator penalized appropriate syllabus refusals on unsupported questions for "missing technical detail", whereas the human evaluator rewarded them for adhering to curriculum boundaries. This calibration divergence affirms that automated LLM evaluation cannot substitute for human domain expert validation in educational AI benchmarks.

---

## 10. Discussion
A central finding of this investigation is that Knowledge Graph augmentation did not outperform the unaugmented baseline on human-judged correctness within the audited sample. Several evidence-based hypotheses elucidate this outcome:

1. **Local Model Capacity and Prompt Congestion**: The benchmark utilized a 3-billion-parameter local model (`llama3.2:latest`). Smaller language models have limited instruction-following bandwidth when processing structured context. Injecting multi-hop graph triples into the prompt may have constrained the generator, leading to overly terse responses, whereas the baseline generated free-form explanations leveraging pretraining weights.
2. **Entity Extraction Granularity**: In multi-hop comparison questions (e.g., comparing TCP and UDP flow control), the `TopicExtractor` often retrieved facts anchored to one entity while retrieving sparse context for the other. When provided with asymmetric graph context, the model struggled to synthesize balanced comparisons, whereas the baseline drew upon broad pretraining associations.
3. **Syllabus Concept Familiarity**: Undergraduate computer science concepts (e.g., AVL tree balance factors, stack LIFO operations, OSI layers) are extensively represented in pretraining corpora. For standard curriculum concepts, foundation models already possess high parametric memorization, diminishing the incremental factual advantage of external retrieval.
4. **Scoring Penalty on Refusals**: On unsupported curriculum questions, the human rubric evaluated whether the question was answered correctly. Because KG-RAG delivered conservative refusals while the baseline generated plausible technical essays, the baseline accrued higher surface correctness points on technical content, despite violating curriculum boundaries.

These observations indicate that the value of Knowledge Graph RAG in education lies primarily in structural navigation and boundary enforcement rather than basic factual recall on standard syllabus concepts.

---

## 11. Limitations
The findings of this study must be interpreted within the context of specific limitations:
1. **Model Architecture Discrepancy**: The evaluation was executed using a local 3B model (`llama3.2:latest`) to guarantee local reproducibility. However, the production deployment of EduGraphAI employs Groq Cloud API with `llama-3.3-70b-versatile`. Frontier 70B models handle structured context with substantially greater fidelity; hence, these results reflect local constrained execution rather than peak production capability.
2. **Absence of Document-RAG Comparison**: A standardized, multi-subject unstructured textbook corpus was unavailable in the repository. Consequently, the study evaluates KG-RAG strictly against an LLM-only baseline and does not compare Knowledge Graphs against dense passage vector retrieval.
3. **Audit Sample Size**: While the benchmark spans 120 questions, the double-blind human audit evaluated 30 stratified items. Subgroup analyses for unsupported queries ($n=6$) and individual subjects ($n=5$) possess limited statistical power.

---

## 12. Threats to Validity
- **Internal Validity**: Entity extraction heuristics could introduce retrieval noise. Evaluator subjectivity was mitigated through double-blinding, randomized presentation, and pre-registered rubrics, but individual stylistic preferences may persist.
- **External Validity**: Evaluations were restricted to six undergraduate computer science subjects. Results may differ in non-STEM domains where concept taxonomies are less formalized.
- **Construct Validity**: Measuring "factual grounding" independently of "correctness" on an ordinal 0–3 scale presents inherent overlap, as factual errors degrade perceived correctness.
- **Statistical Validity**: Non-parametric tests and Holm-Bonferroni correction were strictly applied to protect against Type I error inflation across multiple comparisons.

---

## 13. Future Work
Grounding future directions directly in our empirical findings, we identify the following priorities:
1. **Production Frontier Model Benchmarking**: Replicate the double-blind evaluation using `llama-3.3-70b-versatile` via Groq to assess whether larger models better leverage structured graph context.
2. **Hybrid Graph-Dense Retrieval**: Develop a hybrid architecture coupling Neo4j relational traversal with dense vector passage search over primary textbooks.
3. **Dynamic Graph-Confidence Filtering**: Implement adaptive gating where graph context is injected only when entity retrieval confidence exceeds an empirical threshold, falling back to parametric generation for high-confidence core concepts.
4. **Sub-Graph Pruning**: Refine Cypher query synthesis to prune redundant relational neighbors and alleviate prompt congestion on small models.
5. **Graph Retrieval Latency Optimization**: Implement Redis caching for frequently traversed concept subgraphs to mitigate the $2.34\times$ latency overhead.
6. **Large-Scale Multi-Rater Human Audit**: Expand the human audit sample to $N \ge 100$ evaluated by multiple independent faculty raters to establish inter-rater reliability.
7. **Curriculum Guardrail Fine-Tuning**: Explicitly fine-tune smaller language models to recognize graph-absence signals and formulate pedagogical redirections without penalizing answer depth.

---

## 14. Conclusion
This study evaluated EduGraphAI, a Knowledge Graph-grounded educational retrieval-augmented generation system, against an unaugmented language model baseline across 120 standardized computer science examination queries. Through a double-blind, paired human audit with Holm-Bonferroni multiplicity correction, we found that Knowledge Graph augmentation did not improve human-judged answer correctness on a small local model (`llama3.2`), with the unaugmented baseline achieving a statistically significantly higher correctness score ($2.600$ vs. $2.133$, $p = 0.0088$). Educational relevance and factual grounding showed no statistically significant differences after multiplicity correction, and both systems achieved near-ceiling gold-fact coverage ($>93\%$). On out-of-scope queries, KG-RAG demonstrated directional exploratory utility in enforcing curriculum boundaries, but incurred a substantial $2.34\times$ latency penalty.

These findings demonstrate that **incorporating a Knowledge Graph into an educational QA system does not automatically translate into higher answer quality**. Educational AI architects must carefully weigh retrieval precision, model capacity, latency costs, and syllabus boundary objectives when designing retrieval-augmented systems.

---

## References
1. Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems (NeurIPS)*, 33, 9459-9474.
2. Pan, S., et al. (2024). Unifying Large Language Models and Knowledge Graphs: A Roadmap. *IEEE Transactions on Knowledge and Data Engineering*, 36(7), 3580-3599.
3. Ji, Z., et al. (2023). Survey of Hallucination in Natural Language Generation. *ACM Computing Surveys*, 55(12), 1-38.
4. Wilcoxon, F. (1945). Individual Comparisons by Ranking Methods. *Biometrics Bulletin*, 1(6), 80-83.
5. Holm, S. (1979). A Simple Sequentially Rejective Multiple Test Procedure. *Scandinavian Journal of Statistics*, 6(2), 65-70.
6. Efron, B., & Tibshirani, R. J. (1994). *An Introduction to the Bootstrap*. CRC Press.
7. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*. Lawrence Erlbaum Associates.
8. Neo4j Graph Database Documentation. (2024). Cypher Query Language Reference, Version 5.
