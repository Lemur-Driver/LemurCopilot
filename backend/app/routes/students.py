from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.database import client, sessions_collection, students_collection
from app.dependencies import get_current_student
from app.models import Student
from app.services.llm_service import generate_text

router = APIRouter(
    prefix="/students",
    tags=["students"],
)

class PromptRequest(BaseModel):
    prompt: str

class QuizAnswer(BaseModel):
    question: str
    selectedIndex: int
    correctIndex: int
    isCorrect: bool

class QuizResultRequest(BaseModel):
    topic: str
    answers: list[QuizAnswer] = Field(default_factory=list)

@router.get("/me", response_model=Student)
async def get_me(student: Student = Depends(get_current_student)):
    return student

@router.get("/me/mastery")
async def get_mastery(student: Student = Depends(get_current_student)):
    return {"mastery": student.mastery}

@router.post("/me/quiz-results")
async def save_quiz_result(request: QuizResultRequest, student: Student = Depends(get_current_student)):
    now = datetime.utcnow()
    total = len(request.answers)
    score = sum(answer.isCorrect for answer in request.answers) / total if total else 0.0
    current = student.mastery.get(request.topic)
    attempts = (current.attempts if current else 0) + 1
    previous_best = (current.best_score if current and current.best_score is not None else current.score if current else 0.0)
    best_score = max(score, previous_best)
    await students_collection.update_one(
        {"_id": ObjectId(student.id)},
        {
            "$set": {
                f"mastery.{request.topic}.score": score,
                f"mastery.{request.topic}.last_score": score,
                f"mastery.{request.topic}.best_score": best_score,
                f"mastery.{request.topic}.last_seen": now,
            },
            "$inc": {f"mastery.{request.topic}.attempts": 1},
            "$addToSet": {
                f"mastery.{request.topic}.failed_questions": {
                    "$each": [
                        answer.question
                        for answer in request.answers
                        if not answer.isCorrect
                    ]
                },
            },
        },
    )
    await sessions_collection.insert_one({
        "student_id": ObjectId(student.id), "started_at": now,
        "quiz_topic": request.topic, "score": score,
        "answers": [answer.model_dump() for answer in request.answers],
    })
    return {"topic": request.topic, "score": score, "attempts": attempts}

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