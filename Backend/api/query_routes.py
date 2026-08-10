from fastapi import APIRouter, Depends
from pydantic import BaseModel

from llm.rag_service import RAGService
from database.auth import get_current_user
from database.models import User


router = APIRouter(
    prefix="/query",
    tags=["Knowledge Graph Query"]
)


class QueryRequest(BaseModel):
    question: str


@router.post("/")
def ask_question(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):

    response = RAGService.answer(
        request.question
    )

    return response