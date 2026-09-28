from bson import ObjectId
from fastapi import Depends, Header, HTTPException

from app.database import students_collection
from app.models import Student
from app.services.token_service import decode_access_token


async def get_current_student(authorization: str | None = Header(default=None)) -> Student:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Se requiere autenticación")

    token = authorization[7:].strip()
    try:
        student_id = decode_access_token(token)
        if not ObjectId.is_valid(student_id):
            raise ValueError("ID inválido")
        document = await students_collection.find_one({"_id": ObjectId(student_id)})
    except (ValueError, TypeError):
        document = None

    if document is None:
        raise HTTPException(status_code=401, detail="Token inválido o estudiante no encontrado")

    return Student.model_validate(document)
