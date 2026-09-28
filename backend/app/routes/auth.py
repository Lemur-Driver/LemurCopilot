from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.auth_service import (
    InvalidGoogleTokenError,
    extract_user_profile,
    upsert_student_from_google,
    verify_google_id_token,
)

from app.services.token_service import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


class GoogleAuthRequest(BaseModel):
    credential: str


class GoogleAuthResponse(BaseModel):
    id: str
    google_sub: str
    email: str
    name: str
    picture: str | None
    access_token: str
    token_type: str = "bearer"

@router.post("/google", response_model=GoogleAuthResponse)
async def google_auth(request: GoogleAuthRequest):
    try:
        claims = verify_google_id_token(request.credential)
    except InvalidGoogleTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Token de Google inválido: {exc}") from exc

    profile = extract_user_profile(claims)
    student = await upsert_student_from_google(profile)

    return GoogleAuthResponse(
        id=student.id,
        google_sub=student.google_sub,
        email=student.email,
        name=student.name,
        picture=student.picture,
        access_token=create_access_token(student.id),
    )