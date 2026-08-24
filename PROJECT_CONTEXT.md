# EduGraphAI — Project Context

## 1. Project Overview

EduGraphAI is a knowledge graph-based question answering system for educational content.

The goal is to organize educational learning material into a structured knowledge graph containing concepts and relationships, then use that graph to retrieve relevant information for user questions and support grounded answer generation.

The system is intended to reduce unsupported or hallucinated answers by grounding responses in structured educational knowledge.

---

## 2. Project Domain

Domain: Education

Primary use case:

- Students ask questions about educational subjects.
- The system identifies relevant concepts/topics.
- Relevant information is retrieved from the educational knowledge graph.
- The retrieved context is used to support the final answer.
- The system also contains features related to graph visualization, learning paths, recommendations, history, bookmarks, and user interaction.

---

## 3. Current Subjects / Knowledge Graph Data

Educational subjects currently represented in the project data include:

- Algorithms and Data Structures (ADA)
- Computer Networks (CN)
- Data Structures and Algorithms (DSA)
- Machine Learning (ML)
- Operating Systems (OS)
- Software Engineering and Project Management (SEPM)

Subject-wise node and edge datasets have been prepared.

Merged datasets currently include:

- `master_nodes.csv`
- `master_edges.csv`

---

## 4. Knowledge Graph

Database:

- Neo4j
- Cypher

Previously recorded knowledge graph size:

- Nodes: 464
- Relationships: 743

The graph represents educational concepts and relationships between concepts.

The graph is intended to provide structured context for question answering.

IMPORTANT:
The node/relationship counts must be updated if the graph changes significantly.

---

## 5. High-Level Architecture

Educational Learning Material
        |
        v
Data Preparation
        |
        v
Concept / Relationship Data
        |
        v
Node + Edge CSVs
        |
        v
Neo4j Knowledge Graph
        |
        v
User Question
        |
        v
Query Processing
        |
        v
Concept / Intent Identification
        |
        v
Graph Retrieval
        |
        v
Relevant Educational Context
        |
        v
Answer Generation
        |
        v
Frontend

---

## 6. Repository Structure

Current major project areas:

```text
Knowledge_Graph_Project/
│
├── Backend/
│
├── data/
│
├── SCRIPTS/
│
├── frontend/
│
├── .gitignore
│
└── PROJECT_CONTEXT.md