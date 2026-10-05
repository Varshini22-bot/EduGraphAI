# EduGraphAI

**Knowledge-Graph-Grounded Question Answering System for Educational Content**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-edu--graph--ai.vercel.app-success?style=for-the-badge&logo=vercel&logoColor=white)](https://edu-graph-ai.vercel.app/)
[![Backend Status](https://img.shields.io/badge/Backend-Render%20Cloud-informational?style=for-the-badge&logo=render&logoColor=white)](https://edugraphai-backend.onrender.com/health)
[![Database](https://img.shields.io/badge/Database-Neo4j%20AuraDB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://console.neo4j.io/)
[![Lighthouse Audit](https://img.shields.io/badge/Lighthouse-100%25%20A11y%20%7C%20100%25%20SEO-brightgreen?style=for-the-badge&logo=googlechrome&logoColor=white)](https://pagespeed.web.dev/analysis/https-edu-graph-ai-vercel-app/s9kniyxn2b?form_factor=desktop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 1. Overview

**EduGraphAI** is an AI-powered educational question answering and learning platform designed to help computer science students, educators, and academic evaluators explore complex academic curricula through structured, knowledge-graph-grounded explanations.

### The Educational Problem
Traditional conversational AI systems rely on unconstrained parametric memory. When asked academic or exam-oriented questions, generic language models frequently:
* Drift outside established university syllabi.
* Omit crucial conceptual prerequisites and dependency hierarchies.
* Invent plausible-sounding but unverified algorithmic relationships.
* Fail to tailor explanations to academic grading criteria (e.g., standard 2-mark definitions vs. 10-mark structured breakdowns).

### The Knowledge Graph Solution
EduGraphAI addresses this challenge by grounding question answering in an explicit **Neo4j Knowledge Graph**. Rather than generating text in isolation, the system:
1. Identifies core academic entities from student questions.
2. Traverses semantic relationships in the curriculum graph (such as prerequisites, constituent sub-concepts, and applications).
3. Injects structured graph context into the language model prompt.
4. Generates cohesive, curriculum-grounded educational answers accompanied by interactive visual concept maps.

This grounding ensures that students receive answers aligned with accredited course structures while visually exploring how academic concepts connect.

---

## 2. Key Features

### 🎓 Educational Question Answering
* **Knowledge-Graph-Grounded QA**: Responses are synthesized conditioned on explicit graph entities and relationship triples.
* **Curriculum-Aware Retrieval**: Exact and fuzzy entity matching across engineering syllabus topics.
* **Subject Selector**: Filter questions by specific academic subjects or search across the entire curriculum.
* **Concept & Relationship Display**: Every response highlights identified concept nodes and related graph connections.

### 📝 Educational Answer Modes
Students can request explanations tailored to specific academic needs:
* **Explain Simply**: High-level conceptual analogies for intuitive understanding.
* **Short Answer (2-Mark Style)**: Concise formal definitions and key terminology.
* **5-Mark Answer**: Medium-depth explanations covering core working principles.
* **10-Mark Answer**: Comprehensive university-format breakdown including Definition, Need, Working Principle, Algorithm/Pseudocode, Step-by-Step Flow, Complexity Analysis, Advantages/Disadvantages, and Exam Tips.
* **Give Example**: Real-world scenarios and walkthrough demonstrations.
* **Related Concepts**: Adjacent topics and prerequisite chains derived from graph edges.

### 🕸️ Knowledge Graph & Exploration
* **Interactive Concept Map**: Visualized using React Flow, displaying concept nodes, prerequisite hierarchies, and outgoing links.
* **Direct Topic Exploration**: Inspect complete concept subgraphs (`/graph/topic/{topic}`) and immediate neighbors.
* **Curriculum Boundary Handling**: Out-of-curriculum questions receive constructive guidance detailing supported subjects rather than ungrounded speculative answers.

### 💬 Chat Experience
* **Interactive Controls**: One-click actions to *Stop Generating*, *Regenerate*, and *Edit/Resend* queries.
* **Smart Auto-Scroll & Copy**: Smooth scroll tracking during generation and one-click Markdown copy buttons.
* **Client-Side Conversation Sharing**: Instant zero-database sharing via URL-safe Raw Deflate compression tokens (`/share/{token}`).
* **Isolated Guest Mode**: Full access to educational QA and graph visualization without mandatory sign-up.

### 🔐 Authentication & Account Management
* **Student Registration & Login**: Account creation with minimum 8-character password enforcement.
* **JWT Session Management**: Standard OAuth2 Bearer token authentication.
* **Authentication Rate Limiting**: Built-in sliding-window protection on login and registration endpoints.
* **Account Deactivation Protection**: Inactive user verification at login and credential evaluation.

### 🎨 Modern Responsive UI
* **Design System**: Tailored dark-mode-first aesthetic with accessible high-contrast typography.
* **Mobile Support**: Fully responsive layout with sliding drawer navigation on mobile viewports.
* **Accessible Visualizations**: WCAG AA compliant contrast ratios and keyboard-navigable controls.

---

## 3. System Architecture

```text
                           Student
                              │
                              ▼
                   Next.js 14 Frontend
                (Vercel Edge CDN / React Flow)
                              │
                              ▼ HTTPS / REST
                   FastAPI Backend
                    (Render Cloud)
                              │
             ┌────────────────┴────────────────┐
             │                                 │
             ▼                                 ▼
      Question Processing             Knowledge Graph
     & Entity Extraction                 Retrieval
             │                                 │
             │                                 ▼
             │                           Neo4j AuraDB
             │                        (Encrypted Bolt)
             │                                 │
             └────────────────┬────────────────┘
                              │
                              ▼
                      Retrieved Context
                   (Concepts + Relations)
                              │
                              ▼
                          Groq LLM
                  (llama-3.3-70b-versatile)
                              │
                              ▼
                      Grounded Answer
                              │
                              ▼
                         Student UI
```

### End-to-End Execution Flow
1. **Student Question**: Student submits an inquiry (e.g., *"Explain Binary Search for 8 marks"*).
2. **Entity & Intent Extraction**: Topic extractor resolves candidate curriculum topics and marks/depth requirements.
3. **Graph Retrieval**: Cypher queries retrieve the central node, definitions, prerequisite dependencies (`PREREQUISITE_FOR`, `DEPENDS_ON`), and adjacent relationships.
4. **Context Construction**: Extracted graph triples and syllabus constraints are assembled into an augmented prompt.
5. **LLM Generation**: Groq cloud inference engine generates structured educational prose anchored to the retrieved context.
6. **Frontend Rendering**: Next.js renders structured Markdown with syntax-highlighted code, LaTeX equations, and interactive graph topology.

---

## 4. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | Next.js 14 (App Router), React 18, TypeScript | Client-side user interface, state management, routing |
| **Frontend Styling** | Tailwind CSS | Modern responsive design with light/dark adaptive themes |
| **Graph Visualization**| React Flow (`@xyflow/react`), Dagre | Node-link concept graphs and layout calculation |
| **Backend Framework** | FastAPI, Python 3.14, Uvicorn | High-performance asynchronous REST API |
| **Validation & ORM** | Pydantic v2, SQLAlchemy | Strict request validation, settings parsing, SQLite ORM |
| **Knowledge Graph** | Neo4j AuraDB (Cloud), Neo4j Python Driver | Semantic storage of curriculum entities and relations |
| **LLM Provider** | Groq API (`llama-3.3-70b-versatile`) | Fast, structured educational response generation |
| **Local LLM Fallback** | Ollama (`llama3.2`) | Local development without external API costs |
| **Authentication** | OAuth2 Bearer, JWT (`python-jose`, `passlib`) | Token-based stateless authentication |
| **Application DB** | SQLite | User credentials and conversation metadata |
| **Frontend Hosting** | Vercel | Global CDN distribution with edge caching |
| **Backend Hosting** | Render | Managed container hosting with continuous integration |

---

## 5. Knowledge Graph

The EduGraphAI knowledge graph represents academic knowledge as a directed, labeled property graph:

* **Nodes**: Represent distinct curriculum entities (e.g., Subjects, Modules, Concepts, Algorithms, Data Structures).
* **Edges (Relationships)**: Represent pedagogical dependencies and structural ties:
  * `PREREQUISITE_FOR`: Strict conceptual dependency order.
  * `DEPENDS_ON`: Functional requirements between concepts.
  * `USES`: Algorithmic techniques applied by an entity.
  * `PART_OF`: Hierarchical module or unit containment.
  * `TYPE_OF`: Categorical taxonomy relationships.
  * `HAS_TOPIC`: Subject-to-topic ownership.

### Verified Production Snapshot
* **Total Nodes**: `474`
* **Total Relationships**: `972`

*(Note: These figures represent the verified production snapshot of the current curriculum graph and may evolve as additional modules are integrated).*

---

## 6. Supported Academic Subjects

EduGraphAI is currently grounded in six fundamental undergraduate Computer Science & Engineering subjects:

| Code | Subject Name | Key Covered Topics |
| :--- | :--- | :--- |
| **DSA** | Data Structures & Algorithms | Arrays, Linked Lists, Binary Trees, AVL Trees, Graphs, Quick Sort, Merge Sort |
| **ADA** | Analysis & Design of Algorithms | Asymptotic Analysis, Divide & Conquer, Greedy Strategies, Dynamic Programming |
| **CN** | Computer Networks | OSI Model, TCP/IP Suite, Flow Control, Sliding Window Protocols, Routing, DNS |
| **ML** | Machine Learning | Supervised Learning, Linear Regression, Decision Trees, Logistic Regression |
| **OS** | Operating Systems | Process Scheduling, Deadlock, Banker's Algorithm, Paging, Virtual Memory |
| **SEPM** | Software Engineering & Project Management | SDLC Models, Agile Methodologies, Software Testing, Quality Assurance |

---

## 7. Production Deployment & Live Endpoints

* **Frontend URL**: [https://edu-graph-ai.vercel.app/](https://edu-graph-ai.vercel.app/) (Vercel)
* **Backend API Base**: [https://edugraphai-backend.onrender.com](https://edugraphai-backend.onrender.com) (Render)
* **Knowledge Graph**: Neo4j AuraDB Cloud (Encrypted Bolt Protocol)
* **Primary LLM**: Groq Cloud (`llama-3.3-70b-versatile`)

### Monitoring & Health Check Endpoints

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/health` | `GET` | High-level system health monitoring (graph database and LLM configuration). |
| `/graph/health` | `GET` | Operational diagnostics (connection latency, active target, AuraDB pause state; URIs and credentials redacted). |
| `/stats` | `GET` | Real-time counts of active graph nodes and relationships. |
| `/ask` | `GET` | Primary question answering query endpoint with optional topic context. |
| `/query` | `POST` | Structured JSON request endpoint for educational question answering. |
| `/graph/topic/{topic}` | `GET` | Subgraph retrieval for a specific curriculum concept. |
| `/graph/neighbors/{topic}` | `GET` | Adjacent outgoing and incoming conceptual connections. |

---

## 8. Security & Reliability Hardening

EduGraphAI incorporates multi-layered security controls implemented and verified across production audits:

* **Production JWT Secret Validation**: Startup executes a strict fail-fast check; missing or default placeholder secrets trigger an immediate `RuntimeError` in production (`DEBUG=False`).
* **Inactive Account Blocking**: Login authentication and bearer token dependency resolution reject inactive accounts (`is_active == False`) with standard uniform error messages.
* **Password Policy**: New user registration enforces a minimum password length of 8 characters via schema validation.
* **Authentication Rate Limiting**: Dedicated in-memory sliding-window limiter on `/auth/login` and `/auth/register` (5 attempts / minute / client IP) with standard `Retry-After` HTTP 429 headers.
* **Infrastructure Redaction**: Public health probes and connection logs redact internal hostnames, connection strings, database identifiers, and credentials.
* **Parameterized Cypher Queries**: Graph operations use parameterized queries to prevent Cypher injection vulnerabilities.
* **CORS Origin Whitelisting**: Strict origin controls restrict cross-origin browser requests to the official Vercel domain and local developer instances.

---

## 9. Local Development Setup

Follow these steps to run EduGraphAI locally for development or evaluation:

### 1. Prerequisites
* **Python**: 3.10 to 3.14
* **Node.js**: 18+ and `npm`
* **Neo4j**: Local instance (Neo4j Desktop / Community) or free [Neo4j AuraDB](https://console.neo4j.io/)
* **LLM**: Free [Groq API Key](https://console.groq.com/) or local [Ollama](https://ollama.ai/) instance

### 2. Clone the Repository
```bash
git clone https://github.com/Varshini22-bot/EduGraphAI.git
cd EduGraphAI
```

### 3. Backend Setup
```bash
cd Backend

# Create and activate Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
cp .env.example .env
```

Configure `Backend/.env` with your development values:
```ini
DEBUG=true
JWT_SECRET_KEY=dev-secret-key-for-local-runs-only-replace-in-production-1234

# Neo4j Settings (Local or AuraDB)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j
NEO4J_MODE=auto

# LLM Configuration (Groq or Ollama)
LLM_PROVIDER=groq
LLM_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile

# Alternatively, for local offline Ollama:
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3.2
# OLLAMA_BASE_URL=http://localhost:11434
```

Start the backend API server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
*Backend API available at: `http://localhost:8000` (Docs at `http://localhost:8000/docs`).*

### 4. Frontend Setup
```bash
cd ../frontend

# Install Node dependencies
npm install

# Create environment configuration
cp .env.example .env.local
```

Configure `frontend/.env.local`:
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the Next.js development server:
```bash
npm run dev
```
*Frontend application available at: `http://localhost:3000`.*

---

## 10. Repository Structure

```text
EduGraphAI/
├── Backend/
│   ├── api/                    # FastAPI route definitions (routes, auth_routes, graph_routes)
│   ├── database/               # SQLAlchemy models, schemas, crud, and auth utilities
│   ├── evaluation/             # Research benchmark scripts, datasets, and audit reports
│   │   ├── baselines/          # Baseline runner implementations
│   │   ├── results/            # Statistical analysis and camera-ready figures
│   │   └── eval_dataset.json   # 120-question multi-subject benchmark dataset
│   ├── graph/                  # Neo4j connection pool, graph service, and recommendation
│   ├── llm/                    # RAG service, topic extractor, and LLM prompt builder
│   ├── tests/                  # Automated unit and integration test suites
│   ├── utils/                  # In-memory rate limiter and statistics helpers
│   ├── app.py                  # FastAPI application entrypoint
│   ├── config.py               # Environment configuration and security validation
│   └── requirements.txt        # Python backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js 14 App Router (chat, login, signup, share, settings)
│   │   ├── components/         # Modular React components (chat, graph, sidebar, navbar)
│   │   ├── context/            # React context providers (Auth, Settings, Toast)
│   │   └── lib/                # API clients, compression utilities, and TypeScript types
│   ├── package.json            # Frontend npm dependencies and build scripts
│   └── tsconfig.json           # TypeScript configuration
│
├── data/                       # Curriculum datasets across 6 subjects
│   ├── ADA/                    # Analysis & Design of Algorithms nodes/edges
│   ├── CN/                     # Computer Networks nodes/edges
│   ├── DSA/                    # Data Structures & Algorithms nodes/edges
│   ├── ML/                     # Machine Learning nodes/edges
│   ├── OS/                     # Operating Systems nodes/edges
│   └── SEPM/                   # Software Engineering nodes/edges
│
├── EDUGRAPHAI_RELEASE_SNAPSHOT.md # Production release snapshot
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## 11. Research & Evaluation Summary

EduGraphAI was systematically evaluated in an academic study comparing Knowledge-Graph-Grounded RAG (KG-RAG) against an unaugmented Large Language Model baseline across a 120-question computer science curriculum dataset, supplemented by an $N=30$ double-blind human audit.

### Validated Findings
* **Educational Relevance**: Both KG-RAG and the unaugmented baseline achieved comparable educational relevance ratings on curriculum topics (paired mean difference $-0.200$, Wilcoxon $W = 9.0$, Holm-adjusted $p = 0.250$), indicating both generated pedagogically applicable content.
* **Factual Grounding**: Both systems sustained high factual grounding across core syllabus topics. Although unadjusted metrics suggested a nominal difference, the difference was not statistically significant after Holm-Bonferroni correction ($p = 0.079 > 0.05$).
* **Curriculum Gold-Fact Coverage**: On supported syllabus topics ($n=24$), both systems exhibited near-ceiling fact coverage: KG-RAG achieved 93.3% aggregate coverage (56/60 facts), compared to 100.0% for the baseline (paired difference not statistically significant, $p = 0.250$).
* **Out-of-Scope Handling**: On out-of-syllabus queries ($n=6$), KG-RAG exhibited descriptive guardrail behavior, refusing unsupported topics with higher mean restraint (2.167 vs. 1.333), directing students to supported subjects.
* **Generator Style & Fluency**: When evaluated with small local models (`llama3.2`), unconstrained generation produced longer, more elaborative prose that scored higher in subjective human fluency ratings, whereas graph-augmented synthesis produced structured, concise answers.
* **Retrieval Latency Trade-Off**: Graph-augmented generation required additional computational overhead (mean latency of 47.29 s vs. 20.19 s for the baseline on local test runtimes), representing the processing cost of entity extraction, Cypher traversals, and context injection.

---

## 12. Known Limitations & Future Improvements

To ensure transparent academic reporting, current architectural limitations are documented below:

* **Render Free-Tier Cold Starts**: The backend service on Render's free tier spins down after 15 minutes of inactivity. Initial wake-up requests incur an approximate 50-second latency.
* **AuraDB Free-Tier Pause Behavior**: Neo4j AuraDB Free instances auto-pause after 3 consecutive days of zero database activity. Instances can be resumed in approximately 60 seconds.
* **Guest History Persistence**: Unauthenticated guest conversation history is managed in browser memory and does not persist across full page reloads.
* **Client-Side Token Storage**: Authenticated JWT tokens are stored in browser `localStorage`. For enterprise production environments, migration to `HttpOnly` `SameSite=Lax` cookies is recommended.
* **In-Memory Rate Limiting**: The sliding-window rate limiter is instance-local and resets if the backend dyno restarts.
* **Manual Password Recovery**: Automated email dispatch for self-service password reset is disabled in the demo deployment; administrator assistance is required for account resets.
* **Database Architecture**: User management relies on SQLite, suitable for the current single-instance deployment but requiring migration to PostgreSQL for horizontally scaled clusters.

---

## 13. Research Reproducibility

Researchers wishing to inspect or reproduce evaluation benchmarks can locate the primary artifacts in the repository:

* **Benchmark Dataset**: `Backend/evaluation/eval_dataset.json` (120 curated questions across 6 subjects).
* **Automated Runner**: `Backend/evaluation/run_benchmark.py` and `evaluate_quality.py`.
* **Statistical Validation Scripts**: `Backend/evaluation/validate_part_9k_statistics.py` and `analyze_results.py`.
* **Human Audit Data**: `Backend/evaluation/human_audit_sample.csv` and `Backend/evaluation/results/HUMAN_AUDIT_FINAL_REPORT.md`.
* **Camera-Ready Figures & Data**: `Backend/evaluation/results/figures/` and `FIGURE_SOURCE_DATA.md`.

---

## 14. Project Status

```text
Current Status: Deployed and operational

Frontend: Vercel (https://edu-graph-ai.vercel.app/)
Backend: Render (https://edugraphai-backend.onrender.com)
Knowledge Graph: Neo4j AuraDB Cloud (Connected)
LLM Provider: Groq Cloud (llama-3.3-70b-versatile)
Supported Subjects: DSA, ADA, CN, ML, OS, SEPM
Verified Graph Snapshot: 474 nodes, 972 relationships
Current Git Baseline: main (synchronized)
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) — free for academic, non-commercial, and educational research use.
