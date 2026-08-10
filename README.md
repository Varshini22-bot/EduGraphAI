# EduGraphAI

## Knowledge Graph-Based Question Answering System for Educational Content

EduGraphAI is a knowledge graph-based educational question answering system designed to organize academic learning content into structured concepts and relationships.

The system combines **Knowledge Graphs, Neo4j, Python, natural language query processing, LLM-based answer generation, and a Next.js frontend** to provide an interactive platform for exploring educational concepts.

The project is designed to ground educational question answering in structured knowledge extracted from learning materials rather than relying only on unstructured text generation.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Knowledge Graph](#knowledge-graph)
- [Educational Subjects](#educational-subjects)
- [Data Pipeline](#data-pipeline)
- [Query Processing](#query-processing)
- [Answer Generation](#answer-generation)
- [Frontend](#frontend)
- [Backend](#backend)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Current Development Status](#current-development-status)
- [Evaluation](#evaluation)
- [Future Enhancements](#future-enhancements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [GitHub Development Workflow](#github-development-workflow)
- [Project Goals](#project-goals)
- [Author](#author)

---

# Overview

Educational content contains a large number of interconnected concepts, definitions, topics, and relationships. Traditional question-answering systems may not explicitly represent these relationships, making it difficult to understand how concepts are connected.

EduGraphAI addresses this problem by representing educational knowledge as a **Knowledge Graph**.

The system follows the general workflow:

```text
Educational Content
        |
        v
Data Preparation
        |
        v
Concepts + Relationships
        |
        v
Knowledge Graph
        |
        v
Neo4j
        |
        v
User Question
        |
        v
Query Processing
        |
        v
Topic / Concept Identification
        |
        v
Graph Retrieval
        |
        v
Relevant Knowledge
        |
        v
Answer Generation
        |
        v
Interactive Frontend

The project is currently under development, with the core knowledge graph, backend structure, and frontend structure already established.

Problem Statement

Students often work with large volumes of educational material containing interconnected concepts.

For example, a student learning Computer Networks may need to understand relationships between:

Computer Networks
       |
       +-- TCP
       |
       +-- UDP
       |
       +-- IP
       |
       +-- Routing
       |
       +-- Transport Layer

A structured Knowledge Graph can represent these connections explicitly.

EduGraphAI aims to use this structured representation to support educational question answering and concept exploration.

Objectives

The main objectives of EduGraphAI are:

Convert educational learning material into structured knowledge.
Extract important educational concepts.
Represent concepts as nodes in a Knowledge Graph.
Represent relationships between concepts as graph edges.
Store and query the graph using Neo4j.
Process natural-language educational questions.
Identify relevant topics from user queries.
Retrieve relevant information from the Knowledge Graph.
Use retrieved information to support answer generation.
Provide an interactive educational web interface.
Support learning-oriented features such as related topics, learning paths, history, bookmarks, and graph visualization.
Key Features
Knowledge Graph
Structured representation of educational concepts.
Concept-to-concept relationships.
Neo4j-based graph storage and querying.
Subject-wise educational datasets.
Master node and relationship datasets.
Query Processing

The backend contains query-processing functionality for processing educational questions and identifying relevant topics.

For example:

Input:
"What is normalization?"

Processed topic:
"normalization"

The current implementation provides a basic topic extraction mechanism, which is intended to be extended as the project develops.

Graph Querying

The backend contains functionality for interacting with the Neo4j Knowledge Graph and retrieving graph information relevant to educational topics.

Answer Generation

The project contains LLM-related backend components and prompt-building functionality intended to use retrieved educational knowledge as context for generating answers.

Graph Visualization

The application contains graph visualization functionality to support exploration of relationships between educational concepts.

Learning Support

The frontend contains components for:

Learning paths
Recommendations
Related topics
Progress information
Bookmarks
Question history
User Interface

The Next.js frontend contains pages and components for:

Login
Signup
Forgot Password
Dashboard
Profile
Settings
Chat-based interaction
System Architecture
                         +----------------------+
                         | Educational Content  |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |  Data Preparation    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Nodes + Relationships|
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Knowledge Graph      |
                         |      Neo4j           |
                         +----------+-----------+
                                    |
                                    |
                         +----------v-----------+
                         |    User Question     |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |  Query Processing    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Topic / Concept      |
                         | Identification       |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |   Graph Retrieval    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Relevant Graph       |
                         | Context              |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Answer Generation    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Next.js Frontend     |
                         +----------------------+
Knowledge Graph

EduGraphAI uses Neo4j as the graph database.

The Knowledge Graph consists of:

Nodes

Nodes represent educational concepts, topics, or other entities extracted from learning materials.

Relationships

Relationships represent connections between educational concepts.

The project maintains both subject-specific datasets and merged datasets.

Current Recorded Graph Size

The currently recorded Knowledge Graph contains:

464 Nodes
743 Relationships

These values represent the graph state recorded during development and may increase as additional educational data is incorporated.

Educational Subjects

The current project contains educational datasets for multiple subjects:

Subject	Abbreviation
Algorithms and Data Structures	ADA
Computer Networks	CN
Data Structures and Algorithms	DSA
Machine Learning	ML
Operating Systems	OS
Software Engineering and Project Management	SEPM

The data is maintained using subject-wise node and relationship datasets.

The project also contains merged datasets:

master_nodes.csv
master_edges.csv
Data Pipeline

The educational data preparation workflow follows:

Educational Learning Material
            |
            v
       Data Collection
            |
            v
      Data Preparation
            |
            v
     Concept Extraction
            |
            v
       Node Creation
            |
            v
    Relationship Creation
            |
            v
        CSV Files
            |
            v
  Master Node / Edge Files
            |
            v
       Neo4j Database

The project contains scripts for data preparation and validation, including functionality for:

Checking missing nodes
Merging subject datasets
Preparing master datasets
Query Processing

EduGraphAI contains a backend query-processing component.

The current topic extraction logic performs basic processing such as:

Converting the question to lowercase.
Removing common question phrases.
Removing the question mark.
Returning the remaining topic text.

For example:

"What is normalization?"

is transformed into:

"normalization"

Similarly:

"Explain machine learning?"

can be processed into:

"machine learning"

The query-processing component is part of the larger pipeline and is still being developed toward more robust educational question understanding.

Graph Retrieval

After processing a user question, the system is intended to identify relevant concepts and retrieve corresponding information from the Neo4j Knowledge Graph.

The retrieval workflow is:

User Question
      |
      v
Query Processing
      |
      v
Extracted Topic
      |
      v
Neo4j Query
      |
      v
Relevant Nodes
      |
      v
Relevant Relationships
      |
      v
Graph Context

The backend contains graph-query-related modules responsible for interacting with the knowledge graph.

Answer Generation

EduGraphAI contains backend components for LLM interaction and prompt construction.

The intended answer-generation workflow is:

User Question
      |
      v
Query Processing
      |
      v
Knowledge Graph Retrieval
      |
      v
Relevant Educational Context
      |
      v
Prompt Construction
      |
      v
LLM
      |
      v
Educational Answer

The objective is to use retrieved educational context to support the generated answer.

The answer-generation pipeline is currently under development and will be validated through end-to-end testing.

Frontend

The frontend is developed using:

Next.js
React
TypeScript
Tailwind CSS

The application contains several pages and reusable components.

Application Pages
Dashboard
Login
Signup
Forgot Password
Profile
Settings
Main Components
AnswerCard
BookmarkList
ConfirmDialog
GraphViewer
HistoryList
LearningPath
Navbar
PricingModal
ProgressDashboard
Recommendations
RelatedTopics
Sidebar
Toggle
UpgradeDialog
UsageIndicator
Chat Components
ChatBubble
ChatHistory
ChatInput
ChatMessage
ConversationContainer
QuickActions
ResponseActions
TypingIndicator
Context and Utilities
AuthContext
SettingsContext
ToastContext
API utilities
Authentication utilities
Storage utilities
Metrics utilities
Voice input
Shared types
Backend

The backend is implemented using Python and contains components for application handling, graph interaction, query processing, LLM interaction, and educational features.

Important backend modules include:

app.py
config.py
graph_query.py
graph_visualizer.py
learning_path.py
llm.py
load_topics.py
neo4j_connection.py
prompt_builder.py
query_graph.py
query_processor.py
stats.py
topic_extractor.py
Backend Responsibilities

The backend is responsible for areas such as:

Application/API handling
Neo4j database connectivity
Graph querying
Query processing
Topic extraction
Prompt construction
LLM interaction
Graph visualization data
Learning path functionality
Topic loading
Application statistics
Technology Stack
Programming Languages
Python
TypeScript
JavaScript
Backend
Python
Neo4j
Cypher
Natural Language Processing
LLM integration
Frontend
Next.js
React
TypeScript
Tailwind CSS
Database
Neo4j
Data
CSV
Educational datasets
Knowledge Graph node and relationship datasets
Development Tools
VS Code
Git
GitHub
Project Structure
Knowledge_Graph_Project/
│
├── Backend/
│   ├── app.py
│   ├── config.py
│   ├── graph_query.py
│   ├── graph_visualizer.py
│   ├── learning_path.py
│   ├── llm.py
│   ├── load_topics.py
│   ├── neo4j_connection.py
│   ├── prompt_builder.py
│   ├── query_graph.py
│   ├── query_processor.py
│   ├── stats.py
│   └── topic_extractor.py
│
├── data/
│   ├── ADA/
│   ├── CN/
│   ├── DSA/
│   ├── ML/
│   ├── OS/
│   ├── SEPM/
│   ├── master_nodes.csv
│   └── master_edges.csv
│
├── SCRIPTS/
│   ├── check_missing_nodes.py
│   └── merge_csv.py
│
├── frontend/
│   ├── hooks/
│   ├── services/
│   ├── src/
│   └── utils/
│
├── .gitignore
└── README.md
Current Development Status
Completed
 Educational data collection
 Educational data preparation
 Subject-wise node datasets
 Subject-wise relationship datasets
 Master node dataset
 Master relationship dataset
 Neo4j Knowledge Graph setup
 Backend project structure
 Frontend project structure
 Graph query-related components
 Query processing component
 Topic extraction component
 LLM-related components
 Prompt-building component
 Graph visualization component
 Learning path component
 GitHub repository setup
In Progress
 Complete end-to-end query processing
 Complete graph retrieval workflow
 Complete graph-grounded answer generation
 Connect all backend components
 Complete frontend-backend integration
 End-to-end testing
 System evaluation
 Performance evaluation
 Documentation and screenshots
Evaluation

After completing the system, EduGraphAI will be evaluated using a set of educational questions across the supported subjects.

Potential evaluation areas include:

Query Processing
Correct topic identification
Correct question classification
Handling of different question formats
Knowledge Graph Retrieval
Correct concept retrieval
Relevant relationship retrieval
Retrieval precision
Retrieval recall
Answer Generation
Answer relevance
Answer correctness
Context grounding
Unsupported information
System Performance
Query processing time
Graph retrieval time
Overall response latency

Actual evaluation metrics will be added after the system has been tested.

No accuracy, precision, recall, F1-score, latency, or hallucination-reduction percentage is claimed until it has been experimentally measured.

Future Enhancements

Potential future improvements include:

More advanced natural-language query processing
Improved topic and entity extraction
Query intent classification
Better graph traversal and retrieval
Improved graph-context construction
Graph-grounded LLM prompting
Answer-quality evaluation
Automated testing
Performance optimization
Additional educational subjects
Improved graph visualization
Personalized learning paths
Improved recommendations
Enhanced student progress tracking
Installation
Prerequisites

Before running EduGraphAI, install the required software:

Python
Node.js
npm
Neo4j
Git
Clone the Repository
git clone https://github.com/Varshini22-bot/EduGraphAI.git

Navigate into the project:

cd EduGraphAI
Backend Setup

Navigate to the backend:

cd Backend

Create and activate a Python virtual environment if required:

Windows
python -m venv venv
venv\Scripts\activate

Install backend dependencies:

pip install -r requirements.txt

If the project uses a different dependency-management approach, follow the dependency configuration currently present in the backend.

Neo4j Setup

Install and start Neo4j.

Configure the required Neo4j connection settings using environment variables or the project's configuration mechanism.

Typical configuration includes:

NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD

Do not commit database credentials to GitHub.

Frontend Setup

Navigate to the frontend:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

The frontend can then be accessed through the local development URL shown by Next.js.

Environment Variables

Sensitive configuration should be stored in environment files and should never be committed to GitHub.

Example:

NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password

If additional APIs are used by the backend or frontend, their credentials should also be stored using environment variables.

Important

Never commit:

.env
.env.local
.env.development.local
.env.test.local
.env.production.local
Usage

The intended application workflow is:

1. Start Neo4j
        |
2. Start Backend
        |
3. Start Frontend
        |
4. Open EduGraphAI
        |
5. Enter an educational question
        |
6. Query is processed
        |
7. Relevant graph information is retrieved
        |
8. Answer is generated
        |
9. Result is displayed in the frontend

Example questions:

What is normalization?
Explain supervised learning.
What is a deadlock in operating systems?
Explain TCP/IP.
What is the difference between BFS and DFS?
GitHub Development Workflow

EduGraphAI is maintained using Git and GitHub.

After making changes:

git status

Stage changes:

git add .

Commit:

git commit -m "describe your changes"

Push:

git push

Check repository status:

git status

Generated files and sensitive configuration are excluded through .gitignore.

Security and Repository Guidelines

The following should never be committed:

.env
.env.local
API keys
Passwords
Database credentials
Python virtual environments
node_modules
__pycache__
*.pyc
.next
Generated build files

The project uses .gitignore to prevent common generated files and sensitive configuration from being tracked.

Project Goals

The long-term goal of EduGraphAI is to provide an educational platform where students can:

Ask questions using natural language.
Explore concepts and their relationships.
Retrieve information from a structured educational Knowledge Graph.
Receive answers supported by relevant educational context.
Discover related topics.
Explore learning paths.
Track learning activity.
Interact with educational knowledge through an intuitive interface.
Project Status

🚧 EduGraphAI is currently under active development.

The Knowledge Graph, educational datasets, backend architecture, and frontend architecture have been established.

Current development is focused on completing and validating the end-to-end workflow:

User Question
      ↓
Query Processing
      ↓
Knowledge Graph Retrieval
      ↓
Context Construction
      ↓
Answer Generation
      ↓
Frontend Response

Once the complete workflow is stable, the project will undergo systematic testing and evaluation.

Author

Varshini V B

B.E. Artificial Intelligence and Data Science

Repository

GitHub:
https://github.com/Varshini22-bot/EduGraphAI
