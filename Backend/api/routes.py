from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from database.share_service import save_shared_conversation, get_shared_conversation
from llm.rag_service import RAGService

from utils.stats import get_stats


router = APIRouter()


# ============================================================
# REQUEST MODEL
# ============================================================

class QueryRequest(BaseModel):

    question: str
    context_topic: Optional[str] = None


# ============================================================
# ASK QUESTION - OLD GET API
# ============================================================

@router.get("/ask")
def ask(query: str, context_topic: Optional[str] = None):

    if not query or not query.strip():

        return {
            "status": False,
            "query": query,
            "topic": None,
            "answer": "Please enter a valid question or topic.",
            "graph_context": [],
            "incoming": [],
            "learning_path": [],
            "recommendations": []
        }


    try:

        response = RAGService.answer(
            query.strip(),
            context_topic=context_topic.strip() if context_topic else None,
        )

        return response


    except Exception as e:

        print("RAG error:", e)

        return {
            "status": False,
            "query": query,
            "topic": None,
            "answer": "Unable to process the question.",
            "graph_context": [],
            "incoming": [],
            "learning_path": [],
            "recommendations": [],
            "error": str(e)
        }


# ============================================================
# ASK QUESTION - FRONTEND POST API
# ============================================================

@router.post("/query")
def query(request: QueryRequest):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )


    try:

        response = RAGService.answer(
            request.question.strip(),
            context_topic=request.context_topic.strip() if request.context_topic else None,
        )

        return response


    except Exception as e:

        print("RAG error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GRAPH STATISTICS
# ============================================================

@router.get("/stats")
def stats():

    try:

        return get_stats()


    except Exception as e:

        print("Statistics error:", e)

        return {
            "error": "Unable to retrieve graph statistics.",
            "details": str(e)
        }


# ============================================================
# CONVERSATION SHARING ENDPOINTS
# ============================================================

class CreateShareRequest(BaseModel):
    title: str
    topic: Optional[str] = None
    messages: List[Dict[str, Any]]


@router.post("/share")
def create_share(req: CreateShareRequest, db: Session = Depends(get_db)):
    if not req.messages:
        raise HTTPException(
            status_code=400,
            detail="Cannot share an empty conversation."
        )

    share_id = save_shared_conversation(
        db,
        title=req.title,
        topic=req.topic,
        messages=req.messages,
    )

    return {
        "id": share_id,
        "url": f"/share/{share_id}",
    }


@router.get("/share/{share_id}")
def read_share(share_id: str, db: Session = Depends(get_db)):
    shared = get_shared_conversation(db, share_id.strip())
    if not shared:
        raise HTTPException(
            status_code=404,
            detail="Shared conversation not found or expired."
        )
    return shared