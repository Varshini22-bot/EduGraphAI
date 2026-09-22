"""
config.py

Central configuration file for the Knowledge Graph Learning Assistant.
All project-wide settings should be defined here.
"""

import os
from pathlib import Path

# Load secrets from a local .env file for non-Docker (local) runs. This is
# best-effort: python-dotenv is a project dependency, but if it is ever
# absent the import must not crash config loading. Under Docker there is no
# .env inside the image (it is .dockerignore'd) and Compose injects the same
# variables as real environment variables, so this call is simply a no-op
# there. Values already present in the real environment are NOT overridden.
def _load_env_fallback(filepath: Path):
    if not filepath.is_file():
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

backend_env = Path(__file__).resolve().parent / ".env"
root_env = Path(__file__).resolve().parent.parent / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv()
    if backend_env.exists():
        load_dotenv(backend_env)
    if root_env.exists():
        load_dotenv(root_env)
except Exception:
    _load_env_fallback(backend_env)
    _load_env_fallback(root_env)

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

NEO4J_DATABASE = os.getenv(
    "NEO4J_DATABASE",
    "neo4j"
)

# Neo4j Operation Mode:
# - 'auto': Attempt primary (cloud/configured); auto-failover to fallback (local) if primary is paused/down
# - 'cloud': Strictly use primary cloud instance
# - 'local': Strictly use fallback/local instance
NEO4J_MODE = os.getenv("NEO4J_MODE", "auto").lower().strip()

# Fallback Local Neo4j connection (used when primary cloud instance is paused or unreachable)
NEO4J_FALLBACK_URI = os.getenv(
    "NEO4J_FALLBACK_URI",
    "bolt://127.0.0.1:7687"
)
NEO4J_FALLBACK_USERNAME = os.getenv(
    "NEO4J_FALLBACK_USERNAME",
    "neo4j"
)
NEO4J_FALLBACK_PASSWORD = os.getenv(
    "NEO4J_FALLBACK_PASSWORD",
    os.getenv("NEO4J_PASSWORD", "")
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
# LLM Provider Configuration
# ==========================================================
# Provider selection:
# - 'ollama'     : Local Ollama daemon (default for local development)
# - 'openai'     : OpenAI API (or OpenAI-compatible service)
# - 'groq'       : Groq Cloud API (OpenAI-compatible)
# - 'openrouter' : OpenRouter API (OpenAI-compatible)
# - 'gemini'     : Google Gemini API (OpenAI-compatible endpoint)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower().strip()

# Base URL for OpenAI-compatible providers.
_default_base_urls = {
    "openai": "https://api.openai.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai",
}

LLM_BASE_URL = os.getenv("LLM_BASE_URL", _default_base_urls.get(LLM_PROVIDER, ""))
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# Active LLM Model name:
# Defaults to OLLAMA_MODEL if provider is ollama, or standard models for cloud providers
_default_cloud_models = {
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4o-mini",
    "openrouter": "meta-llama/llama-3.2-3b-instruct:free",
    "gemini": "gemini-1.5-flash",
}
LLM_MODEL = os.getenv(
    "LLM_MODEL",
    OLLAMA_MODEL if LLM_PROVIDER == "ollama" else _default_cloud_models.get(LLM_PROVIDER, "llama3.2")
)

# ==========================================================
# FastAPI Configuration
# ==========================================================

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

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
# Frontend & CORS Configuration
# ==========================================================

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Comma-separated list of allowed origins.
# In production, set to your deployed frontend domain(s), e.g. "https://edugraphai.vercel.app"
_cors_origins_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
)
CORS_ORIGINS = [origin.strip() for origin in _cors_origins_raw.split(",") if origin.strip()]

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

DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if DEBUG else "INFO")

# In production mode, issue an explicit warning if running with the insecure default secret key
if not DEBUG and JWT_SECRET_KEY == "knowledge_graph_secret_key_change_this":
    import warnings
    warnings.warn(
        "SECURITY WARNING: Running in production (DEBUG=False) with default insecure JWT_SECRET_KEY! "
        "Please set a cryptographically secure key via the JWT_SECRET_KEY environment variable.",
        UserWarning,
        stacklevel=2,
    )
