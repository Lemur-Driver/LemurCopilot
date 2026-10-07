from datetime import datetime
from zoneinfo import ZoneInfo

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.database import client, exercises_collection, sessions_collection, students_collection
from app.dependencies import get_current_student
from app.models import Student, flatten_mastery, get_mastery_entry
from app.services.llm_service import generate_text
from app.prompts.lesson_prompts import LESSON_CONFIGS
from app.services.progress_service import build_course_progress, PASSING_SCORE

router = APIRouter(
    prefix="/students",
    tags=["students"],
)

class PromptRequest(BaseModel):
    prompt: str

class QuizAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sessionId: str
    exerciseId: str
    selectedIndex: int = Field(ge=0, le=3)

class QuizResultRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sessionId: str

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
        if (get_mastery_entry(student.mastery, lesson_id).best_score if get_mastery_entry(student.mastery, lesson_id) else 0.0) >= PASSING_SCORE
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


@router.post("/me/quiz-answer")
async def submit_quiz_answer(request: QuizAnswerRequest, student: Student = Depends(get_current_student)):
    if not ObjectId.is_valid(request.sessionId) or not ObjectId.is_valid(request.exerciseId):
        raise HTTPException(status_code=400, detail="La sesion o la pregunta no son validas")

    session_id = ObjectId(request.sessionId)
    assignment = await sessions_collection.find_one(
        {
            "_id": session_id,
            "student_id": ObjectId(student.id),
            "quiz_status": "assigned",
        }
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="No existe un quiz activo para esta sesion")

    assigned_ids = [str(exercise_id) for exercise_id in assignment.get("quiz_exercise_ids", [])]
    if request.exerciseId not in assigned_ids:
        raise HTTPException(status_code=400, detail="La pregunta no pertenece a este quiz")

    exercise = await exercises_collection.find_one({
        "_id": ObjectId(request.exerciseId),
        "topic": assignment["quiz_topic"],
    })
    if not exercise:
        raise HTTPException(status_code=404, detail="La pregunta ya no esta disponible")
    if request.selectedIndex >= len(exercise.get("options", [])):
        raise HTTPException(status_code=400, detail="La opcion seleccionada no es valida")

    correct_index = exercise.get("correct_index")
    answer_record = {
        "exercise_id": request.exerciseId,
        "question": exercise["question"],
        "selected_index": request.selectedIndex,
        "correct_index": correct_index,
        "is_correct": request.selectedIndex == correct_index,
        "topic": assignment["quiz_topic"],
    }
    existing_answer = next(
        (
            answer
            for answer in assignment.get("answers", [])
            if answer.get("exercise_id") == request.exerciseId
        ),
        None,
    )
    if existing_answer:
        if existing_answer.get("selected_index") != request.selectedIndex:
            raise HTTPException(status_code=409, detail="La respuesta a esta pregunta ya fue registrada")
    else:
        result = await sessions_collection.update_one(
            {
                "_id": session_id,
                "student_id": ObjectId(student.id),
                "quiz_status": "assigned",
                "answers.exercise_id": {"$ne": request.exerciseId},
            },
            {"$push": {"answers": answer_record}},
        )
        if result.modified_count != 1:
            raise HTTPException(status_code=409, detail="No se pudo registrar la respuesta")
        await exercises_collection.update_one(
            {"_id": ObjectId(request.exerciseId)},
            {"$inc": {"times_correct" if answer_record["is_correct"] else "times_incorrect": 1}},
        )

    return {
        "exerciseId": request.exerciseId,
        "selectedIndex": request.selectedIndex,
        "correctIndex": correct_index,
        "isCorrect": answer_record["is_correct"],
        "explanation": exercise.get("explanation"),
    }


@router.post("/me/quiz-results")
async def save_quiz_result(request: QuizResultRequest, student: Student = Depends(get_current_student)):
    if not ObjectId.is_valid(request.sessionId):
        raise HTTPException(status_code=400, detail="La sesion del quiz no es valida")

    session_id = ObjectId(request.sessionId)
    assignment = await sessions_collection.find_one(
        {
            "_id": session_id,
            "student_id": ObjectId(student.id),
            "quiz_status": "assigned",
        }
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="No existe un quiz activo para esta sesion")

    assigned_ids = [str(exercise_id) for exercise_id in assignment.get("quiz_exercise_ids", [])]
    answers = assignment.get("answers", [])
    if len(assigned_ids) != 3 or {answer.get("exercise_id") for answer in answers} != set(assigned_ids):
        raise HTTPException(status_code=400, detail="Debes responder las tres preguntas antes de finalizar")

    now = datetime.utcnow()
    score = sum(answer["is_correct"] for answer in answers) / len(answers)
    topic = assignment["quiz_topic"]
    current = get_mastery_entry(student.mastery, topic)
    attempts = (current.attempts if current else 0) + 1
    previous_best = (current.best_score if current and current.best_score is not None else current.score if current else 0.0)
    best_score = max(score, previous_best)

    result = await sessions_collection.update_one(
        {"_id": session_id, "student_id": ObjectId(student.id), "quiz_status": "assigned"},
        {"$set": {
            "quiz_status": "completed",
            "completed_at": now,
            "score": score,
        }, "$unset": {"quiz_exercise_ids": ""}},
    )
    if result.modified_count != 1:
        raise HTTPException(status_code=409, detail="Este quiz ya fue enviado")

    await students_collection.update_one(
        {"_id": ObjectId(student.id)},
        {
            "$set": {
                f"mastery.{topic}.score": score,
                f"mastery.{topic}.last_score": score,
                f"mastery.{topic}.best_score": best_score,
                f"mastery.{topic}.last_seen": now,
            },
            "$inc": {f"mastery.{topic}.attempts": 1},
            "$addToSet": {
                f"mastery.{topic}.failed_questions": {
                    "$each": [answer["question"] for answer in answers if not answer["is_correct"]],
                },
            },
        },
    )
    return {
        "sessionId": request.sessionId,
        "topic": topic,
        "score": score,
        "passed": score >= PASSING_SCORE,
        "passingScore": PASSING_SCORE,
        "attempts": attempts,
    }


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