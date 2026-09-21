from fastapi import APIRouter, HTTPException
from graph.graph_service import GraphService
from graph.neo4j_client import check_graph_health

router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"]
)

# ----------------------------------------------------
# Graph Connectivity & Health Diagnostics
# ----------------------------------------------------

@router.get("/health")
def graph_health():
    """
    Returns diagnostics on Knowledge Graph connectivity, active target (cloud vs local failover),
    latency, and whether AuraDB is paused.
    """
    return check_graph_health()


# ----------------------------------------------------
# Get Complete Topic
# ----------------------------------------------------

@router.get("/topic/{topic_name}")
def get_topic(topic_name: str):

    result = GraphService.get_complete_response(topic_name)

    if not result["status"]:
        status_code = 503 if result.get("is_connection_error") else 404
        raise HTTPException(
            status_code=status_code,
            detail=result["message"]
        )

    return result


# ----------------------------------------------------
# Search Topic
# ----------------------------------------------------

@router.get("/search/{keyword}")
def search(keyword: str):

    return GraphService.search(keyword)


# ----------------------------------------------------
# Topic Exists
# ----------------------------------------------------

@router.get("/exists/{topic_name}")
def exists(topic_name: str):

    return {
        "exists": GraphService.topic_exists(topic_name)
    }


# ----------------------------------------------------
# Outgoing Relationships
# ----------------------------------------------------

@router.get("/neighbors/{topic_name}")
def neighbors(topic_name: str):

    return GraphService.get_neighbors(topic_name)


# ----------------------------------------------------
# Incoming Relationships
# ----------------------------------------------------

@router.get("/incoming/{topic_name}")
def incoming(topic_name: str):

    return GraphService.get_incoming(topic_name)