import os
from datetime import datetime, timedelta, timezone

import jwt
from google.genai import types

JWT_ALGORITHM = "HS256"
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", str(7 * 24 * 60)))

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET debe estar definido en el entorno")


def create_access_token(student_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": student_id,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise ValueError("Token inválido o expirado") from exc

    student_id = payload.get("sub")
    if not isinstance(student_id, str) or not student_id:
        raise ValueError("Token sin estudiante")
    return student_id


async def generate_with_gemini(
    prompt: str,
    json_mode: bool = True,
) -> str:
    config = None

    if json_mode:
        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )

    return response.text
