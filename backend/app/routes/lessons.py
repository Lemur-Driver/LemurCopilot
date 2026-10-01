from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.dependencies import get_current_student
from app.models import Student
from app.services.profile_service import build_student_profile

from app.prompts.lesson_prompts import (
    LESSON_CONFIGS,
)

from app.services.content_service import (
    get_topic_chunks,
)

from app.services.lesson_service import (
    generate_lesson,
)

from app.services.question_pool_service import ensure_pool, select_quiz


router = APIRouter(
    prefix="/lessons",
    tags=["lessons"],
)


@router.post(
    "/generate/{topic}"
)
async def create_lesson(
    topic: str,
    student: Student = Depends(get_current_student),
):

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

        chunks = await get_topic_chunks(
            topic
        )

        if not chunks:
            raise ValueError(
                f"No existe contenido en "
                f"MongoDB para {topic}"
            )


        # ====================================================
        # 3. PERFIL Y GENERACIÓN DE LECCIÓN
        # ====================================================

        student_profile = build_student_profile(student, topic)
        lesson_result = (
            await generate_lesson(
                topic=topic,
                chunks=chunks,
                config=config,
                student_profile=student_profile,
            )
        )


        lesson = (
            lesson_result["lesson"]
        )


        # ====================================================
        # 4. GENERAR QUIZ
        # ====================================================

        await ensure_pool(
            student_id=student.id,
            topic=topic,
            lesson=lesson,
            chunks=chunks,
            config=config,
            student_profile=student_profile,
        )
        quiz = await select_quiz(student.id, topic)


        # ====================================================
        # 5. RESPONSE
        # ====================================================

        return {
            "topic": topic,

            "lesson": lesson,

            "quiz": quiz,

            "sources": (
                lesson_result["sources"]
            ),
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