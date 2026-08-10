from fastapi import APIRouter, HTTPException
from graph.graph_service import GraphService

router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"]
)

# ----------------------------------------------------
# Get Complete Topic
# ----------------------------------------------------

@router.get("/topic/{topic_name}")
def get_topic(topic_name: str):

    result = GraphService.get_complete_response(topic_name)

    if not result["status"]:
        raise HTTPException(
            status_code=404,
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