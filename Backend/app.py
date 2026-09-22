from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from api.auth_routes import router as auth_router
from api.graph_routes import router as graph_router

from database.database import engine, Base
from database import models


import logging

from config import (
    CORS_ORIGINS,
    DEBUG,
    LLM_PROVIDER,
    LLM_API_KEY,
)
from graph.neo4j_client import check_graph_health

logger = logging.getLogger(__name__)

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Knowledge Graph Learning Assistant",
    debug=DEBUG,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

app.include_router(auth_router)

app.include_router(graph_router)


@app.get("/")
def root():
    return {
        "message": "Knowledge Graph Learning Assistant Backend Running",
        "status": "online",
    }


@app.get("/health")
def health_check():
    """
    Standardized minimal public health check endpoint for production monitoring.
    Reports high-level operational status without exposing internal infrastructure,
    connection URIs, credentials, hostnames, database names, or model details.
    """
    graph_health = check_graph_health()
    graph_healthy = bool(graph_health.get("healthy", False))

    llm_configured = True
    if LLM_PROVIDER != "ollama" and not (LLM_API_KEY and LLM_API_KEY.strip()):
        llm_configured = False

    is_healthy = graph_healthy and llm_configured

    if not is_healthy:
        logger.warning(
            "Public /health check degraded: graph=%s, llm=%s",
            "healthy" if graph_healthy else "unhealthy",
            "configured" if llm_configured else "misconfigured",
        )

    return {
        "status": "healthy" if is_healthy else "degraded",
        "graph": "healthy" if graph_healthy else "unhealthy",
        "llm": "configured" if llm_configured else "misconfigured",
    }
