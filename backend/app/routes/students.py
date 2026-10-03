from datetime import datetime
from zoneinfo import ZoneInfo

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.database import client, exercises_collection, sessions_collection, students_collection
from app.dependencies import get_current_student
from app.models import Student, flatten_mastery, get_mastery_entry
from app.services.llm_service import generate_text
from app.prompts.lesson_prompts import LESSON_CONFIGS
from app.services.progress_service import build_course_progress

router = APIRouter(
    prefix="/students",
    tags=["students"],
)

class PromptRequest(BaseModel):
    prompt: str

class QuizAnswer(BaseModel):
    exerciseId: str | None = None
    question: str = ""
    selectedIndex: int
    correctIndex: int | None = None
    isCorrect: bool | None = None

class QuizResultRequest(BaseModel):
    topic: str
    answers: list[QuizAnswer] = Field(default_factory=list)

@router.get("/me", response_model=Student)
async def get_me(student: Student = Depends(get_current_student)):
    return student


@router.get("/me/mastery")
async def get_mastery(student: Student = Depends(get_current_student)):
    return {"mastery": flatten_mastery(student.mastery)}


@router.get("/me/course-progress")
async def get_course_progress(
    student: Student = Depends(
        get_current_student
    ),
):
    return {
        "units": build_course_progress(
            student
        )
    }


@router.get("/me/dashboard")
async def get_dashboard(student: Student = Depends(get_current_student)):
    lesson_ids = tuple(LESSON_CONFIGS)
    completed_lessons = sum(
        1
        for lesson_id in lesson_ids
        if (get_mastery_entry(student.mastery, lesson_id).best_score if get_mastery_entry(student.mastery, lesson_id) else 0.0) >= 0.6
    )
    attempted_lessons = sum(
        1
        for lesson_id in lesson_ids
        if (get_mastery_entry(student.mastery, lesson_id).attempts if get_mastery_entry(student.mastery, lesson_id) else 0) > 0
    )
    total_attempts = sum(
        get_mastery_entry(student.mastery, lesson_id).attempts if get_mastery_entry(student.mastery, lesson_id) else 0
        for lesson_id in lesson_ids
    )

    activity_dates: set = set()
    cursor = sessions_collection.find(
        {"student_id": ObjectId(student.id)},
        {"started_at": 1},
    )
    async for session in cursor:
        started_at = session.get("started_at")
        if started_at is not None:
            activity_dates.add(started_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/Santiago")).date())

    today = datetime.now(ZoneInfo("America/Santiago")).date()
    current_streak_days = 0
    latest_activity = max(activity_dates, default=None)
    if latest_activity and (today - latest_activity).days <= 1:
        streak_date = latest_activity
        while streak_date in activity_dates:
            current_streak_days += 1
            streak_date = streak_date.fromordinal(streak_date.toordinal() - 1)

    longest_streak_days = 0
    for activity_date in sorted(activity_dates):
        streak_length = 1
        next_date = activity_date.fromordinal(activity_date.toordinal() + 1)
        while next_date in activity_dates:
            streak_length += 1
            next_date = next_date.fromordinal(next_date.toordinal() + 1)
        longest_streak_days = max(longest_streak_days, streak_length)

    total_lessons = len(lesson_ids)
    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "attempted_lessons": attempted_lessons,
        "total_attempts": total_attempts,
        "preparation": round(completed_lessons / total_lessons * 100) if total_lessons else 0,
        "current_streak_days": current_streak_days,
        "longest_streak_days": longest_streak_days,
        "xp": completed_lessons * 40,
    }


@router.post("/me/quiz-results")
async def save_quiz_result(request: QuizResultRequest, student: Student = Depends(get_current_student)):
    if len(request.answers) != 3:
        raise HTTPException(status_code=400, detail="El quiz debe estar completo antes de guardarse")
    if any(
        not answer.exerciseId or not ObjectId.is_valid(answer.exerciseId)
        for answer in request.answers
    ):
        raise HTTPException(status_code=400, detail="Cada respuesta debe identificar un ejercicio válido")
    if len({answer.exerciseId for answer in request.answers}) != len(request.answers):
        raise HTTPException(status_code=400, detail="Un quiz no puede repetir ejercicios")

    now = datetime.utcnow()
    exercise_ids = [ObjectId(answer.exerciseId) for answer in request.answers]
    exercise_documents = await exercises_collection.find(
        {"_id": {"$in": exercise_ids}, "topic": request.topic},
    ).to_list()
    exercises_by_id = {str(exercise["_id"]): exercise for exercise in exercise_documents}
    if len(exercises_by_id) != len(set(answer.exerciseId for answer in request.answers)):
        raise HTTPException(status_code=400, detail="Uno o más ejercicios no pertenecen a este tema")

    answer_records = []
    for answer in request.answers:
        exercise = exercises_by_id[answer.exerciseId]
        correct_index = exercise.get("correct_index")
        is_correct = answer.selectedIndex == correct_index
        question = exercise["question"]
        await exercises_collection.update_one(
            {"_id": exercise["_id"]},
            {"$inc": {"times_correct" if is_correct else "times_incorrect": 1}},
        )
        answer_records.append({
            "exercise_id": answer.exerciseId,
            "question": question,
            "selected_index": answer.selectedIndex,
            "correct_index": correct_index,
            "is_correct": is_correct,
            "topic": request.topic,
        })

    total = len(answer_records)
    score = sum(answer["is_correct"] for answer in answer_records) / total if total else 0.0
    current = get_mastery_entry(student.mastery, request.topic)
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
                        answer["question"]
                        for answer in answer_records
                        if not answer["is_correct"]
                    ]
                },
            },
        },
    )
    await sessions_collection.insert_one({
        "student_id": ObjectId(student.id), "started_at": now,
        "quiz_topic": request.topic, "score": score,
        "answers": answer_records,
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