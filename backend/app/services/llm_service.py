import json
import os
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

import httpx

from google import genai
from google.genai import types

# ============================================================
# CONFIG
# ============================================================

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "")
LLM_REQUEST_TIMEOUT_SECONDS = float(os.getenv("LLM_REQUEST_TIMEOUT_SECONDS", "300"))
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY", "")
OPENCODE_MODEL = os.getenv("CONTENT_LLM_MODEL", "gpt-6-luna")
OPENCODE_BASE_URL = os.getenv(
    "OPENCODE_BASE_URL",
    "https://opencode.ai/inference/go",
).rstrip("/")
_llm_provider_override: ContextVar[str | None] = ContextVar(
    "llm_provider_override", default=None
)
_opencode_session_override: ContextVar[str | None] = ContextVar(
    "opencode_session_override", default=None
)


@contextmanager
def use_llm_provider(provider: str, session_id: str | None = None) -> Iterator[None]:
    provider_token: Token[str | None] = _llm_provider_override.set(provider)
    session_token: Token[str | None] = _opencode_session_override.set(session_id)
    try:
        yield
    finally:
        _opencode_session_override.reset(session_token)
        _llm_provider_override.reset(provider_token)


def _active_llm_provider() -> str:
    return _llm_provider_override.get() or LLM_PROVIDER


gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# ============================================================
# GEMINI
# ============================================================

async def generate_with_gemini(
    prompt: str,
    json_mode: bool = True,
) -> str:

    if gemini_client is None or not GEMINI_MODEL:
        raise RuntimeError("GEMINI_API_KEY y GEMINI_MODEL son necesarias para Gemini")

    config = None
    if json_mode:
        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )

    response = (
        gemini_client
        .models
        .generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config,
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
    if not OLLAMA_URL or not OLLAMA_MODEL:
        raise RuntimeError("OLLAMA_URL y OLLAMA_MODEL son necesarias para Ollama")

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
            "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "16384")),
        },
    }
    
    if json_mode:
        payload["format"] = "json"


    async with httpx.AsyncClient(timeout=LLM_REQUEST_TIMEOUT_SECONDS) as client:

        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
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
    if not OLLAMA_URL or not OLLAMA_MODEL:
        raise RuntimeError("OLLAMA_URL y OLLAMA_MODEL son necesarias para Ollama")

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
# OPENCODE GO
# ============================================================

async def generate_with_opencode(
    prompt: str,
    json_mode: bool = True,
) -> str:
    if not OPENCODE_API_KEY:
        raise RuntimeError("OPENCODE_API_KEY es necesaria para el proveedor opencode_go")

    payload = {
        "model": OPENCODE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.2,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {OPENCODE_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "LemurCopilotContentWorker/1.0",
        "x-opencode-session": _opencode_session_override.get() or f"lemur-content-{uuid.uuid4()}",
    }
    async with httpx.AsyncClient(timeout=LLM_REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{OPENCODE_BASE_URL}/openai/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("Respuesta inesperada de OpenCode") from error
    if not isinstance(content, str) or not content.strip():
        raise ValueError("OpenCode devolvió una respuesta vacía")
    return content


# ============================================================
# PROVIDER
# ============================================================

async def generate_text(
    prompt: str,
    json_mode: bool = True,
) -> str:

    provider = _active_llm_provider()

    if provider == "ollama":

        return await generate_with_ollama(
            prompt=prompt,
            json_mode=json_mode,
        )


    elif provider == "gemini":

        return await generate_with_gemini(
            prompt=prompt,
            json_mode=json_mode,
        )

    elif provider == "opencode_go":
        return await generate_with_opencode(prompt=prompt, json_mode=json_mode)

    raise ValueError(f"Proveedor LLM no soportado: {provider}")
    
    
#-------------------Streaming
async def stream_text(
    prompt: str,
):
    provider = _active_llm_provider()
    if provider == "ollama":

        async for chunk in stream_with_ollama(
            prompt
        ):
            yield chunk

        return


    if provider == "gemini":

        response = await generate_with_gemini(
            prompt
        )

        yield response

        return


    raise ValueError(
        f"Proveedor LLM no soportado: "
        f"{LLM_PROVIDER}"
    )