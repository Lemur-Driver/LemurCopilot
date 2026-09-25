import json

from app.prompts.lesson_prompts import (
    BASE_QUIZ_PROMPT,
)

from app.services.llm_service import (
    generate_text,
)


# ============================================================
# CONSTRUIR CONTEXTO
# ============================================================

def build_quiz_context(
    chunks: list[dict],
) -> str:

    parts = []

    for chunk in chunks:

        parts.append(
            f"""
PÁGINA: {chunk["page"]}

CONTENIDO:
{chunk["text"]}
"""
        )

    return "\n".join(parts)


# ============================================================
# LIMPIAR RESPUESTA DEL LLM
# ============================================================

def clean_json_response(
    response: str,
) -> str:

    response = response.strip()

    if response.startswith("```json"):
        response = response[7:]

    elif response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    return response.strip()


# ============================================================
# VALIDAR QUIZ
# ============================================================

def validate_quiz_json(
    data: dict,
):

    if "questions" not in data:
        raise ValueError(
            "El quiz no contiene 'questions'"
        )

    questions = data["questions"]

    if not isinstance(
        questions,
        list,
    ):
        raise ValueError(
            "'questions' debe ser una lista"
        )

    if len(questions) != 3:
        raise ValueError(
            "El quiz debe tener exactamente 3 preguntas"
        )

    for index, question in enumerate(
        questions
    ):

        if not isinstance(
            question,
            dict,
        ):
            raise ValueError(
                f"Pregunta {index + 1} inválida"
            )

        required_fields = [
            "question",
            "options",
            "correctAnswer",
            "explanation",
        ]

        for field in required_fields:

            if field not in question:
                raise ValueError(
                    f"Pregunta {index + 1}: "
                    f"falta '{field}'"
                )

        options = question["options"]

        if not isinstance(
            options,
            list,
        ):
            raise ValueError(
                f"Pregunta {index + 1}: "
                "'options' debe ser una lista"
            )

        if len(options) != 4:
            raise ValueError(
                f"Pregunta {index + 1}: "
                "debe tener exactamente "
                "4 alternativas"
            )

        correct_answer = (
            question["correctAnswer"]
        )

        if not isinstance(
            correct_answer,
            int,
        ):
            raise ValueError(
                f"Pregunta {index + 1}: "
                "'correctAnswer' debe ser entero"
            )

        if (
            correct_answer < 0
            or correct_answer > 3
        ):
            raise ValueError(
                f"Pregunta {index + 1}: "
                "'correctAnswer' debe estar "
                "entre 0 y 3"
            )


# ============================================================
# GENERAR QUIZ
# ============================================================

async def generate_quiz(
    topic: str,
    lesson: dict,
    chunks: list[dict],
    config: dict,
):

    # --------------------------------------------------------
    # 1. Contexto oficial
    # --------------------------------------------------------

    context = build_quiz_context(
        chunks
    )


    # --------------------------------------------------------
    # 2. Lección como JSON
    # --------------------------------------------------------

    lesson_json = json.dumps(
        lesson,
        ensure_ascii=False,
        indent=2,
    )


    # --------------------------------------------------------
    # 3. Configuración del quiz
    # --------------------------------------------------------

    quiz_focus = config.get(
        "quiz_focus",
        """
        Evalúa comprensión de los conceptos
        principales de la lección.
        """,
    )


    # --------------------------------------------------------
    # 4. Prompt final
    # --------------------------------------------------------

    prompt = f"""
{BASE_QUIZ_PROMPT}


TEMA:

{topic}


OBJETIVO DE APRENDIZAJE:

{config["learning_goal"]}


ENFOQUE DE LA EVALUACIÓN:

{quiz_focus}


LECCIÓN QUE ACABA DE ESTUDIAR EL ESTUDIANTE:

{lesson_json}


CONTEXTO OFICIAL DEL MANUAL:

{context}


Genera ahora exactamente 3 preguntas.

Recuerda:

- 4 alternativas por pregunta
- una sola respuesta correcta
- correctAnswer entre 0 y 3
- incluye explanation
- devuelve solamente JSON válido
"""


    # --------------------------------------------------------
    # 5. LLM
    # --------------------------------------------------------

    response = await generate_text(
        prompt
    )


    # --------------------------------------------------------
    # 6. Limpiar respuesta
    # --------------------------------------------------------

    cleaned_response = (
        clean_json_response(
            response
        )
    )


    # --------------------------------------------------------
    # 7. Convertir JSON
    # --------------------------------------------------------

    try:

        quiz = json.loads(
            cleaned_response
        )

    except json.JSONDecodeError as error:

        print(
            "\nERROR: Quiz JSON inválido\n"
        )

        print(
            cleaned_response
        )

        raise ValueError(
            "El modelo no devolvió "
            "un quiz JSON válido"
        ) from error


    # --------------------------------------------------------
    # 8. Validar
    # --------------------------------------------------------

    validate_quiz_json(
        quiz
    )


    return quiz