"""
config.py

Central configuration file for the Knowledge Graph Learning Assistant.
All project-wide settings should be defined here.
"""

import os

# Load secrets from a local .env file for non-Docker (local) runs. This is
# best-effort: python-dotenv is a project dependency, but if it is ever
# absent the import must not crash config loading. Under Docker there is no
# .env inside the image (it is .dockerignore'd) and Compose injects the same
# variables as real environment variables, so this call is simply a no-op
# there. Values already present in the real environment are NOT overridden.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

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

NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

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

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
)

# How long Ollama keeps the model loaded in memory after a request.
# Ollama's own default is 5 minutes, after which the model is
# unloaded and the NEXT question pays the full model-load cost
# again before generation even starts. Since this app is used in
# bursts (a student asks a few questions, pauses, asks more), that
# reload was being paid repeatedly. "-1" keeps the model resident.
# Set OLLAMA_KEEP_ALIVE=5m (or 0) on a memory-constrained machine.

OLLAMA_KEEP_ALIVE = os.getenv(
    "OLLAMA_KEEP_ALIVE",
    "-1"
)

# Size of the model's context window, in tokens.
#
# Ollama defaults to ~2048. A grounded prompt for a well-connected
# topic measures ~1100 tokens, and a 10-mark answer is allowed
# 1300 output tokens - together that exceeds 2048, so the prompt
# was being silently truncated and the Knowledge Graph grounding
# at the top of it was the part being dropped. 4096 leaves room
# for the largest prompt plus the largest answer budget.

OLLAMA_NUM_CTX = int(
    os.getenv(
        "OLLAMA_NUM_CTX",
        "4096"
    )
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