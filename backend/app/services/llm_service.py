import json
import os
import httpx

from google import genai

# ============================================================
# CONFIG
# ============================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
)

OLLAMA_URL = os.environ[
    "OLLAMA_URL"
]

OLLAMA_MODEL = os.environ[
    "OLLAMA_MODEL"
]

GEMINI_API_KEY = os.environ[
    "GEMINI_API_KEY"
]

GEMINI_MODEL = os.environ[
    "GEMINI_MODEL"
]


gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# GEMINI
# ============================================================

async def generate_with_gemini(
    prompt: str,
) -> str:

    response = (
        gemini_client
        .models
        .generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
    )

    return response.text


# ============================================================
# OLLAMA
# ============================================================

async def generate_with_ollama(
    prompt: str,
    json_mode: bool = True,
) -> str:

    payload = {
        "model": OLLAMA_MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],

        "stream": False,

        "options": {
            "temperature": 0.2,
        },
    }
    
    if json_mode:
        payload["format"] = "json"


    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        
    if not response.is_success:

        print(
            "\n"
            "ERROR DEVUELTO POR OLLAMA"
            "\n"
        )

        print(
            "Status:",
            response.status_code,
        )

        print(
            "Body:"
        )

        print(
            response.text
        )

        print()


        response.raise_for_status()


    data = response.json()


    return data[
        "message"
    ][
        "content"
    ]

#----------------- Streaming

async def stream_with_ollama(
    prompt: str,
):
    payload = {
        "model": OLLAMA_MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],

        "stream": True,

        "options": {
            "temperature": 0.2,
        },
    }


    async with httpx.AsyncClient(
        timeout=120
    ) as client:

        async with client.stream(
            "POST",
            f"{OLLAMA_URL}/api/chat",
            json=payload,
        ) as response:

            response.raise_for_status()


            async for line in response.aiter_lines():

                if not line:
                    continue


                data = json.loads(
                    line
                )


                content = (
                    data
                    .get("message", {})
                    .get("content", "")
                )


                if content:
                    yield content


                if data.get(
                    "done",
                    False,
                ):
                    break


# ============================================================
# PROVIDER
# ============================================================

async def generate_text(
    prompt: str,
    json_mode: bool = True,
) -> str:

    if LLM_PROVIDER == "ollama":

        return await generate_with_ollama(
            prompt=prompt,
            json_mode=json_mode,
        )


    elif LLM_PROVIDER == "gemini":

        return await generate_with_gemini(
            prompt=prompt,
            json_mode=json_mode,
        )


    raise ValueError(
        f"Proveedor LLM no soportado: "
        f"{LLM_PROVIDER}"
    )
    
    
#-------------------Streaming
async def stream_text(
    prompt: str,
):
    if LLM_PROVIDER == "ollama":

        async for chunk in stream_with_ollama(
            prompt
        ):
            yield chunk

        return


    if LLM_PROVIDER == "gemini":

        response = await generate_with_gemini(
            prompt
        )

        yield response

        return


    raise ValueError(
        f"Proveedor LLM no soportado: "
        f"{LLM_PROVIDER}"
    )