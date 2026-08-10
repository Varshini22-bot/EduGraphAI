from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from llm.rag_service import RAGService

from utils.stats import get_stats


router = APIRouter()


# ============================================================
# REQUEST MODEL
# ============================================================

class QueryRequest(BaseModel):

    question: str


# ============================================================
# ASK QUESTION - OLD GET API
# ============================================================

@router.get("/ask")
def ask(query: str):

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
            query.strip()
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
            request.question.strip()
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