from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.dependencies import get_current_student
from app.models import Student
from app.services.profile_service import build_student_profile
from app.services.progress_service import is_topic_unlocked

from app.prompts.lesson_prompts import LESSON_CONFIGS
from app.services.content_release_service import get_published_release_id
from app.services.content_service import get_topic_chunks
from app.services.lesson_service import generate_lesson
from app.services.question_pool_service import select_quiz


router = APIRouter(
    prefix="/lessons",
    tags=["lessons"],
)


@router.post("/{topic}/quiz")
async def create_quiz(
    topic: str,
    student: Student = Depends(get_current_student),
):
    if not is_topic_unlocked(student, topic):
        raise HTTPException(
            status_code=403,
            detail="Debes completar la unidad anterior antes de acceder a esta clase.",
        )
    if topic not in LESSON_CONFIGS:
        raise HTTPException(status_code=404, detail=f"No existe configuración pedagógica para {topic}")

    release_id = await get_published_release_id(topic)
    if not release_id:
        raise HTTPException(
            status_code=503,
            detail=f"No hay contenido publicado para {topic}. Ejecuta el worker y publica el release.",
        )
    try:
        return {"quiz": await select_quiz(student.id, topic, release_id)}
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error))
    except Exception as error:
        print("\nERROR ASIGNANDO QUIZ\n", type(error).__name__, error)
        raise HTTPException(status_code=500, detail="No se pudo preparar el quiz.") from error


@router.post(
    "/generate/{topic}"
)
async def create_lesson(
    topic: str,
    student: Student = Depends(
        get_current_student
    ),
):

    if not is_topic_unlocked(
        student,
        topic,
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Debes completar la unidad "
                "anterior antes de acceder "
                "a esta clase."
            ),
        )

    try:

        # ====================================================
        # 1. CONFIGURACIÓN PEDAGÓGICA
        # ====================================================

        config = LESSON_CONFIGS.get(
            topic
        )

        if config is None:
            raise ValueError(
                f"No existe configuración "
                f"pedagógica para {topic}"
            )


        # ====================================================
        # 2. CONTENIDO DEL MANUAL
        # ====================================================

        chunks = await get_topic_chunks(topic)
        if not chunks:
            raise ValueError(f"No existe contenido en MongoDB para {topic}")

        # ====================================================
        # 3. GENERAR LECCIÓN
        # ====================================================

        student_profile = build_student_profile(student, topic)
        lesson_result = await generate_lesson(
            topic=topic,
            chunks=chunks,
            config=config,
            student_profile=student_profile,
        )
        lesson = lesson_result["lesson"]


        # ====================================================
        # 4. RESPONSE
        # ====================================================

        return {
            "topic": topic,

            "lesson": lesson,

            "sources": lesson_result["sources"],
        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:

        print(
            "\nERROR GENERANDO LECCIÓN\n"
        )

        print(
            type(error).__name__
        )

        print(
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo generar "
                "la lección."
            ),
        )