from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_service import search_manual


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