"""
config.py

Central configuration file for the Knowledge Graph Learning Assistant.
All project-wide settings should be defined here.
"""

import os

# ==========================================================
# Neo4j Configuration
# ==========================================================

NEO4J_URI = os.getenv(
    "NEO4J_URI",
    "bolt://127.0.0.1:7687"
)

NEO4J_USERNAME = os.getenv(
    "NEO4J_USERNAME",
    "neo4j"
)

NEO4J_PASSWORD = os.getenv(
    "NEO4J_PASSWORD",
    "Varshi1234"
)

# ==========================================================
# Ollama Configuration
# ==========================================================

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2"
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

# ==========================================================
# FastAPI Configuration
# ==========================================================

FASTAPI_HOST = "127.0.0.1"
FASTAPI_PORT = 8000

API_TITLE = "Knowledge Graph Learning Assistant API"
API_VERSION = "1.0.0"

# ==========================================================
# JWT Authentication
# ==========================================================

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "knowledge_graph_secret_key_change_this"
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# ==========================================================
# Frontend Configuration
# ==========================================================

FRONTEND_URL = "http://localhost:3000"

# ==========================================================
# Graph Visualization
# ==========================================================

GRAPH_HTML = "../frontend/assets/graph.html"

# ==========================================================
# Topic Matching
# ==========================================================

TOPIC_MATCH_THRESHOLD = 70

# ==========================================================
# Application Settings
# ==========================================================

DEBUG = True

LOG_LEVEL = "INFO"