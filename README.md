# EduGraphAI 🎓🕸️

### Knowledge Graph-Based Question Answering System for Educational Content

[![Live Demo](https://img.shields.io/badge/Live%20Demo-edu--graph--ai.vercel.app-success?style=for-the-badge&logo=vercel&logoColor=white)](https://edu-graph-ai.vercel.app/)
[![Backend Status](https://img.shields.io/badge/Backend-Render%20Cloud-informational?style=for-the-badge&logo=render&logoColor=white)](https://edugraphai-backend.onrender.com/health)
[![Database](https://img.shields.io/badge/Database-Neo4j%20AuraDB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://console.neo4j.io/)
[![Lighthouse Audit](https://img.shields.io/badge/Lighthouse-100%25%20A11y%20%7C%20100%25%20SEO-brightgreen?style=for-the-badge&logo=googlechrome&logoColor=white)](https://pagespeed.web.dev/analysis/https-edu-graph-ai-vercel-app/s9kniyxn2b?form_factor=desktop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**EduGraphAI** is an AI-powered, knowledge graph-grounded educational question answering and learning assistance platform. It transforms computer science and engineering curricula into a structured semantic knowledge graph, empowering students to master complex academic topics, explore prerequisite chains, and visualize conceptual relationships.

Unlike conventional chatbots that rely strictly on unstructured LLM recall, EduGraphAI anchors every explanation in an explicit **Neo4j Knowledge Graph** to eliminate hallucinations, enforce exam-tailored structure, and dynamically render interactive node-link concept maps.

---

## 🌐 Live Deployments

| Component | Platform | Status | Live Link |
| :--- | :--- | :---: | :--- |
| **Frontend Web App** | Vercel | 🟢 Active | [https://edu-graph-ai.vercel.app/](https://edu-graph-ai.vercel.app/) |
| **Backend REST API** | Render | 🟢 Active | [https://edugraphai-backend.onrender.com](https://edugraphai-backend.onrender.com) |
| **API Health Endpoint** | Render | 🟢 Active | [https://edugraphai-backend.onrender.com/health](https://edugraphai-backend.onrender.com/health) |
| **Graph Database** | Neo4j AuraDB Cloud | 🟢 Active | Encrypted Bolt Protocol (`neo4j+s://`) |

---

## ⚡ Key Highlights & Features

* **🧠 Knowledge Graph Retrieval (Neo4j)**: Maps academic entities, definitions, sub-concepts, and dependencies across 6 core Computer Science subjects.
* **📝 Exam-Tailored Response Engine**: Automatically adapts formatting based on question marks/intent (2-mark definitions, 5-mark summaries, 8/10/16-mark university exam breakdowns with definitions, algorithms, diagrams, and complexity analysis).
* **🕸️ Interactive Graph Visualizer**: Built with React Flow; visualizes concept nodes, prerequisite hierarchies (`DEPENDS_ON`, `PREREQUISITE_FOR`), and related topics directly inside the browser.
* **🧭 Curriculum Learning Paths**: Generates progressive, step-by-step topic mastery sequences derived directly from graph relationships.
* **📊 Progress Dashboard & Bookmarks**: Tracks session mastery, studied concepts, topic coverage metrics, and saved bookmarks across student sessions.
* **🛡️ Zero Truncation & Session Isolation**: Up to 4096 output tokens with strict anti-drift contextual anchoring; supports both authenticated and private guest workflows with zero cross-contamination.
* **⚡ 100/100 Lighthouse & Accessibility Rating**: Optimized with zero render-blocking delays, sub-second Core Web Vitals (FCP 0.7s, LCP 0.7s, CLS 0), and full WCAG AA contrast compliance.

---

## 📚 Supported Academic Subjects

EduGraphAI models structured relationships across core engineering domains:

```
                    ┌─────────────────────────┐
                    │      EduGraphAI         │
                    │     Knowledge Graph     │
                    └────────────┬────────────┘
                                 │
     ┌──────────────┬────────────┼────────────┬──────────────┐
     │              │            │            │              │
┌────┴───┐     ┌────┴───┐   ┌────┴───┐   ┌────┴───┐     ┌────┴───┐
│  DSA   │     │  ADA   │   │   CN   │   │   OS   │     │   ML   │
└────────┘     └────────┘   └────────┘   └────────┘     └────────┘
                                 │
                            ┌────┴───┐
                            │  SEPM  │
                            └────────┘
```

1. **Data Structures & Algorithms (DSA)**: Arrays, Linked Lists, Trees, Graphs, Sorting, Dynamic Programming.
2. **Analysis & Design of Algorithms (ADA)**: Asymptotic Notations, Divide & Conquer, Greedy Strategies, Backtracking, NP-Completeness.
3. **Computer Networks (CN)**: OSI Model, TCP/IP Suite, Flow/Congestion Control, Routing Protocols, Network Security.
4. **Operating Systems (OS)**: Process Scheduling, Synchronization, Deadlocks, Memory Management, Virtual Memory, File Systems.
5. **Machine Learning (ML)**: Supervised/Unsupervised Learning, Regression, Classification, Neural Networks, Model Evaluation.
6. **Software Engineering & Project Management (SEPM)**: SDLC Models, Agile, Requirements Engineering, Software Testing, Quality Assurance.

---

## 🏗️ System Architecture

```text
  User Browser (Next.js 14 / Tailwind CSS)
                   │
                   ▼  HTTPS / REST
  ┌──────────────────────────────────────────────────┐
  │         Backend Application (Flask / REST)       │
  │                                                  │
  │  1. Query Processor & Intent Classifier          │
  │     - Topic Resolution                           │
  │     - Mark/Intent Extraction (2/5/8/10/16 marks) │
  │                                                  │
  │  2. Graph Retrieval Engine (Cypher)              │
  │     - Subgraph Extraction & Prerequisite Lookup  │
  │                                                  │
  │  3. Context Builder & Prompt Synthesizer         │
  │     - Grounding Context Injection                │
  │                                                  │
  │  4. LLM Response Generator                       │
  │     - Structured Explanations (up to 4096 tokens)│
  └──────────────┬────────────────────────┬──────────┘
                 │                        │
                 ▼ Bolt/TLS               ▼ HTTPS
      ┌────────────────────┐    ┌────────────────────┐
      │  Neo4j AuraDB      │    │  Google Gemini /   │
      │  Knowledge Graph   │    │  Groq LLM Engine   │
      └────────────────────┘    └────────────────────┘
```

### End-to-End Workflow
1. **Query Processing**: The student submits a query (e.g., *"Explain Binary Search for 8 marks"*). The query processor identifies candidate topics and determines mark intent.
2. **Graph Context Retrieval**: Cypher queries retrieve the concept node, definitions, prerequisite topics, child nodes, and adjacent relationship edges from Neo4j.
3. **Grounded Prompt Construction**: Structured graph facts are formatted into an explicit system prompt, preventing hallucinated connections.
4. **Answer Generation**: The LLM constructs a complete, cohesive answer following academic criteria (Definition $\rightarrow$ Algorithm $\rightarrow$ Complexity $\rightarrow$ Example).
5. **Interactive UI Delivery**: The frontend renders the structured markdown response, generates actionable follow-up questions, and displays the interactive graph subgraph.

---

## 📊 Performance & Lighthouse Benchmarks

Audited on the live production frontend (`https://edu-graph-ai.vercel.app/`):

| Metric | Score | Industry Standard | Status |
| :--- | :---: | :---: | :---: |
| **Accessibility (WCAG AA)** | **100 / 100** | $\ge 90$ | 🟢 Perfect |
| **Search Engine Optimization (SEO)**| **100 / 100** | $\ge 90$ | 🟢 Perfect |
| **Best Practices** | **100 / 100** | $\ge 90$ | 🟢 Perfect |
| **First Contentful Paint (FCP)** | **0.7 s** | $< 1.8\text{ s}$ | 🟢 Instant |
| **Largest Contentful Paint (LCP)** | **0.7 s** | $< 2.5\text{ s}$ | 🟢 Instant |
| **Total Blocking Time (TBT)** | **0 ms** | $< 200\text{ ms}$ | 🟢 Zero Lag |
| **Cumulative Layout Shift (CLS)** | **0.000** | $< 0.1$ | 🟢 Stable |

---

## 🛠️ Technology Stack

### Frontend
* **Framework**: [Next.js 14](https://nextjs.org/) (App Router, React 18, TypeScript)
* **Styling**: [Tailwind CSS](https://tailwindcss.com/) with full Dark/Light adaptive themes
* **Graph Visualization**: [React Flow (@xyflow/react)](https://reactflow.dev/) & [Dagre](https://github.com/dagrejs/dagre)
* **Icons & Rendering**: Lucide React, React Markdown, KaTeX Math rendering
* **Hosting**: [Vercel](https://vercel.com/) (Edge CDN with global SSL)

### Backend
* **Runtime**: [Python 3.14](https://www.python.org/)
* **Framework**: [Flask](https://flask.palletsprojects.com/) / Flask-CORS
* **Graph Database Driver**: [Neo4j Python Driver](https://neo4j.com/developer/python/) (Bolt+Routing)
* **LLM Orchestration**: Google GenAI SDK (`google-genai` / Gemini 2.5) & Groq API Fallback
* **Hosting**: [Render](https://render.com/) (PaaS with automated continuous deployment)

### Database & Storage
* **Graph Database**: [Neo4j AuraDB Cloud](https://neo4j.com/cloud/aura/)
* **Session Storage**: LocalStorage with account-scoped and guest-isolated keys

---

## 📁 Repository Structure

```text
Knowledge_Graph_Project/
├── Backend/
│   ├── app.py                  # Primary Flask REST API entry point
│   ├── config.py               # Production configuration & environment loaders
│   ├── graph_query.py          # Cypher query builder & graph retrieval logic
│   ├── graph_visualizer.py     # Graph data transformation for React Flow
│   ├── learning_path.py        # Prerequisite graph traversals for curricula
│   ├── llm.py                  # LLM integration (Gemini & Groq fallbacks)
│   ├── load_topics.py          # Topic index loader & synonym mappings
│   ├── neo4j_connection.py     # Resilient Neo4j connection pool
│   ├── prompt_builder.py       # Graph-grounded prompt engineering
│   ├── query_processor.py      # Natural language query parsing & intent classification
│   ├── requirements.txt        # Backend Python dependencies
│   ├── stats.py                # Graph analytics & relationship counts
│   └── topic_extractor.py      # Fuzzy & keyword entity extraction
│
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router (layout, page, auth, settings)
│   │   ├── components/         # UI Components (Sidebar, Navbar, AnswerCard, etc.)
│   │   │   └── chat/           # Chat-specific components (ChatInput, ChatBubble, etc.)
│   │   ├── context/            # React Contexts (Auth, Settings, Toast)
│   │   ├── lib/                # API client, metrics, storage, TypeScript types
│   │   └── styles/             # Global CSS & Tailwind configuration
│   ├── package.json            # Node.js dependencies & scripts
│   └── tsconfig.json           # TypeScript compiler configuration
│
├── data/                       # Curated datasets for all 6 subjects
│   ├── ADA/                    # Analysis & Design of Algorithms nodes/edges
│   ├── CN/                     # Computer Networks nodes/edges
│   ├── DSA/                    # Data Structures & Algorithms nodes/edges
│   ├── ML/                     # Machine Learning nodes/edges
│   ├── OS/                     # Operating Systems nodes/edges
│   ├── SEPM/                   # Software Engineering nodes/edges
│   ├── master_nodes.csv        # Consolidated concepts dataset
│   └── master_edges.csv        # Consolidated relationships dataset
│
├── SCRIPTS/                    # Automation & validation scripts
│   ├── check_missing_nodes.py  # Integrity check for graph edges
│   └── merge_csv.py            # Subject dataset merger
│
├── .gitignore                  # Production exclusion rules
└── README.md                   # Project documentation
```

---

## 🚀 Local Installation & Setup

### 1. Prerequisites
* Python 3.10+ (Python 3.11/3.12/3.14 supported)
* Node.js 18+ & npm
* A free [Neo4j AuraDB](https://console.neo4j.io/) instance or local Neo4j Desktop
* A free [Google Gemini API Key](https://aistudio.google.com/) or [Groq API Key](https://console.groq.com/)

### 2. Clone Repository
```bash
git clone https://github.com/Varshini22-bot/EduGraphAI.git
cd EduGraphAI
```

### 3. Backend Setup
```bash
cd Backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `Backend/.env`:
```ini
NEO4J_URI=neo4j+s://<your-auradb-instance-id>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<your-auradb-password>
GEMINI_API_KEY=<your-gemini-api-key>
# Optional fallback:
GROQ_API_KEY=<your-groq-api-key>
PORT=5000
```

Start the backend:
```bash
python app.py
```
*API runs at `http://localhost:5000`.*

### 4. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
```

Edit `frontend/.env.local`:
```ini
NEXT_PUBLIC_API_URL=http://localhost:5000
```

Start the Next.js development server:
```bash
npm run dev
```
*Web application opens at `http://localhost:3000`.*

---

## 📡 API Reference

### 1. Ask Question
```http
POST /ask
Content-Type: application/json

{
  "query": "Explain Binary Search for 8 marks",
  "history": []
}
```
**Response**:
```json
{
  "topic": "Binary Search",
  "subject": "Data Structures & Algorithms",
  "answer": "### 1. Definition\nBinary Search is a divide-and-conquer...",
  "prerequisites": ["Arrays", "Linear Search"],
  "related_topics": ["Divide and Conquer", "Time Complexity"],
  "learning_path": [
    {"step": 1, "topic": "Arrays"},
    {"step": 2, "topic": "Linear Search"},
    {"step": 3, "topic": "Binary Search"}
  ]
}
```

### 2. Retrieve Graph Subgraph
```http
POST /graph
Content-Type: application/json

{
  "topic": "Binary Search"
}
```
**Response**:
```json
{
  "nodes": [
    {"id": "Binary Search", "label": "Binary Search", "type": "Concept"},
    {"id": "Arrays", "label": "Arrays", "type": "Prerequisite"}
  ],
  "edges": [
    {"source": "Arrays", "target": "Binary Search", "relationship": "PREREQUISITE_FOR"}
  ]
}
```

### 3. Service Health
```http
GET /health
```
**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## 👩‍💻 Author & Academic Affiliation

**Varshini V B**  
*B.E. — Artificial Intelligence and Data Science*  
*Department of Artificial Intelligence and Data Science*  

* **GitHub**: [@Varshini22-bot](https://github.com/Varshini22-bot)  
* **Repository**: [Varshini22-bot/EduGraphAI](https://github.com/Varshini22-bot/EduGraphAI)  
* **Live Application**: [https://edu-graph-ai.vercel.app/](https://edu-graph-ai.vercel.app/)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) — free to use and adapt for academic and educational research.
