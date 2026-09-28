import json

from fastapi.responses import StreamingResponse
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
    prepare_chat_response,
)

from app.services.llm_service import (
    stream_text,
)


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


# ============================================================
# REQUEST
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

    history: list[
        ChatMessage
    ] = Field(
        default_factory=list
    )


# ============================================================
# RESPONSE
# ============================================================

class ChatSource(BaseModel):

    topic: str | None = None

    title: str | None = None

    page: int | None = None

    score: float | None = None


class ChatResponse(BaseModel):

    answer: str

    sources: list[
        ChatSource
    ] = Field(
        default_factory=list
    )


# ============================================================
# ENDPOINT
# ============================================================

@router.post(
    "/stream",
)
async def chat_stream(
    request: ChatRequest,
):

    history = [
        message.model_dump()
        for message
        in request.history
    ]


    try:

        prepared = await prepare_chat_response(
            message=request.message,
            history=history,
        )


    except Exception as error:

        print(
            "\nERROR PREPARANDO STREAM\n"
        )

        print(
            repr(error)
        )


        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo preparar "
                "la respuesta."
            ),
        ) from error


    async def generate():

        # ====================================================
        # 1. FUENTES
        # ====================================================

        yield (
            json.dumps(
                {
                    "type":
                        "sources",

                    "sources":
                        prepared["sources"],
                },
                ensure_ascii=False,
            )
            + "\n"
        )


        # ====================================================
        # 2. RESPUESTA DIRECTA
        # ====================================================

        if prepared[
            "direct_answer"
        ] is not None:

            yield (
                json.dumps(
                    {
                        "type":
                            "token",

                        "content":
                            prepared[
                                "direct_answer"
                            ],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


            yield (
                json.dumps(
                    {
                        "type":
                            "done"
                    }
                )
                + "\n"
            )

            return


        # ====================================================
        # 3. STREAM LLM
        # ====================================================

        try:

            async for chunk in stream_text(
                prepared["prompt"]
            ):

                yield (
                    json.dumps(
                        {
                            "type":
                                "token",

                            "content":
                                chunk,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )


        except Exception as error:

            print(
                "\nERROR DURANTE STREAM\n"
            )

            print(
                repr(error)
            )


            yield (
                json.dumps(
                    {
                        "type":
                            "error",

                        "message":
                            "Error generando la respuesta.",
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

            return


        yield (
            json.dumps(
                {
                    "type":
                        "done"
                }
            )
            + "\n"
        )


    return StreamingResponse(
        generate(),
        media_type=(
            "application/x-ndjson"
        ),
        headers={
            "Cache-Control":
                "no-cache",

            "X-Accel-Buffering":
                "no",
        },
    )