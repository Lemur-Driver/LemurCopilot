from typing import Literal

from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import (
    BaseModel,
    Field,
)

from app.services.chat_service import (
    generate_chat_response,
)


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


# ============================================================
# MODELOS
# ============================================================

class ChatMessage(BaseModel):
    role: Literal[
        "user",
        "assistant",
    ]

    content: str = Field(
        min_length=1,
        max_length=2000,
    )


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=500,
    )

    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    answer: str


# ============================================================
# ENDPOINT
# ============================================================

@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
):

    try:

        history = [
            message.model_dump()
            for message
            in request.history
        ]


        answer = await generate_chat_response(
            message=request.message,
            history=history,
        )


        return ChatResponse(
            answer=answer
        )


    except Exception as error:

        print(
            "\nERROR EN CHAT\n"
        )

        print(
            repr(error)
        )


        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo generar "
                "la respuesta del chat."
            ),
        ) from error