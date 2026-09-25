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

        # Obliga a Ollama a responder
        # utilizando JSON válido.
        "format": "json",

        "options": {
            # Un poco más determinista.
            "temperature": 0.2,
        },
    }


    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=120,
        )


    response.raise_for_status()


    data = response.json()


    return data[
        "message"
    ][
        "content"
    ]


# ============================================================
# PROVIDER
# ============================================================

async def generate_text(
    prompt: str,
) -> str:

    if LLM_PROVIDER == "ollama":

        return await generate_with_ollama(
            prompt
        )


    elif LLM_PROVIDER == "gemini":

        return await generate_with_gemini(
            prompt
        )


    raise ValueError(
        f"Proveedor LLM no soportado: "
        f"{LLM_PROVIDER}"
    )