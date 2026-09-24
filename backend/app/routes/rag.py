from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import search_manual, ask_manual

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


class SearchRequest(BaseModel):
    query: str


@router.post("/search")
async def search(request: SearchRequest):
    results = await search_manual(request.query)

    return {
        "results": results
    }
    
@router.post("/ask")
async def ask(request: SearchRequest):
    result = await ask_manual(request.query)

    return result