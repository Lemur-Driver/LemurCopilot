import os
from datetime import datetime

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pymongo import ReturnDocument

from app.database import students_collection
from app.models import Student

GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]

_google_request = google_requests.Request()


class InvalidGoogleTokenError(Exception):
    """El id_token no es válido: firma incorrecta, expirado, o audiencia distinta a GOOGLE_CLIENT_ID."""


def verify_google_id_token(credential: str) -> dict:
    try:
        claims = id_token.verify_oauth2_token(
            credential,
            _google_request,
            audience=GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        raise InvalidGoogleTokenError(str(exc)) from exc

    if not claims.get("email_verified", False):
        raise InvalidGoogleTokenError("El email de la cuenta de Google no está verificado")

    return claims


def extract_user_profile(claims: dict) -> dict:
    return {
        "google_sub": claims["sub"],
        "email": claims["email"],
        "name": claims.get("name") or claims["email"],
        "picture": claims.get("picture"),
    }


async def upsert_student_from_google(profile: dict) -> Student:
    """
    Busca al estudiante por google_sub. Si existe, actualiza sus datos de perfil
    y last_login. Si no existe, lo crea con mastery vacío. google_sub nunca cambia
    una vez creado el documento (es la clave estable de identidad, a diferencia del
    email que en teoría podría variar en la cuenta de Google).
    """
    now = datetime.utcnow()

    result = await students_collection.find_one_and_update(
        {"google_sub": profile["google_sub"]},
        {
            "$set": {
                "email": profile["email"],
                "name": profile["name"],
                "picture": profile["picture"],
                "last_login": now,
            },
            "$setOnInsert": {
                "google_sub": profile["google_sub"],
                "created_at": now,
                "current_unit": None,
                "mastery": {},
            },
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    return Student.model_validate(result)