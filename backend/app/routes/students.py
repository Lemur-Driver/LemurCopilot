from fastapi import APIRouter
from pydantic import BaseModel


from app.database import client
from app.services.llm_service import generate_text

router = APIRouter(
    prefix="/students",
    tags=["students"],
)

class PromptRequest(BaseModel):
    prompt: str

@router.get("/mongo-test")
async def mongo_test():
    await client.admin.command("ping")

    return {"mongodb": "connected"}

@router.get("/llm-test")
async def llm_test():
    response = await generate_text(
        "Explica en una frase qué significa una señal Ceda el Paso."
    )

    return {
        "response": response
    }
    
    
@router.post("/chat")
async def chat(request: PromptRequest):
    response = await generate_text(request.prompt)

    return {
        "response": response
    }