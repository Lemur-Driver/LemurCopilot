from fastapi import (
    APIRouter,
    HTTPException,
)

from app.prompts.lesson_prompts import (
    LESSON_CONFIGS,
)

from app.services.content_service import (
    get_topic_chunks,
)

from app.services.lesson_service import (
    generate_lesson,
)

from app.services.quiz_service import (
    generate_quiz,
)


router = APIRouter(
    prefix="/lessons",
    tags=["lessons"],
)


@router.post(
    "/generate/{topic}"
)
async def create_lesson(
    topic: str,
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
        # 3. GENERAR LECCIÓN
        # ====================================================

        lesson_result = (
            await generate_lesson(
                topic=topic,
                chunks=chunks,
                config=config,
            )
        )


        lesson = (
            lesson_result["lesson"]
        )


        # ====================================================
        # 4. GENERAR QUIZ
        # ====================================================

        quiz = await generate_quiz(
            topic=topic,
            lesson=lesson,
            chunks=chunks,
            config=config,
        )


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