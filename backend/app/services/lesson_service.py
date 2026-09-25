import json

from app.prompts.lesson_prompts import (
    BASE_LESSON_PROMPT,
    LESSON_CONFIGS,
)

from app.services.content_service import (
    get_topic_chunks,
)

from app.services.llm_service import (
    generate_text,
)


# ============================================================
# CONTEXTO
# ============================================================

def build_context(
    chunks: list[dict],
) -> str:

    parts = []

    for chunk in chunks:

        parts.append(
            f"""
FUENTE:
Título: {chunk["title"]}
Página: {chunk["page"]}
Chunk: {chunk["chunk_index"]}

CONTENIDO:
{chunk["text"]}
"""
        )

    return "\n".join(parts)


# ============================================================
# LIMPIAR RESPUESTA
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
# NORMALIZAR RESPUESTA DEL LLM
# ============================================================

def normalize_lesson_json(
    lesson: dict,
) -> dict:

    if not isinstance(
        lesson,
        dict,
    ):
        return lesson


    # --------------------------------------------------------
    # Quitar wrappers comunes
    # --------------------------------------------------------

    for wrapper in [
        "lesson",
        "data",
        "result",
    ]:

        if (
            wrapper in lesson
            and isinstance(
                lesson[wrapper],
                dict,
            )
        ):

            lesson = lesson[wrapper]

            break


    # --------------------------------------------------------
    # key_points es opcional
    # --------------------------------------------------------

    if "key_points" not in lesson:

        lesson["key_points"] = []


    # --------------------------------------------------------
    # Normalizar sections
    # --------------------------------------------------------

    sections = lesson.get(
        "sections"
    )


    if isinstance(
        sections,
        list,
    ):

        for section in sections:

            if not isinstance(
                section,
                dict,
            ):
                continue


            # section_title -> title

            if (
                "title" not in section
                and "section_title" in section
            ):

                section["title"] = (
                    section.pop(
                        "section_title"
                    )
                )


            # heading -> title

            if (
                "title" not in section
                and "heading" in section
            ):

                section["title"] = (
                    section.pop(
                        "heading"
                    )
                )


            # text -> content

            if (
                "content" not in section
                and "text" in section
            ):

                section["content"] = (
                    section.pop(
                        "text"
                    )
                )


            # example es opcional

            if "example" not in section:

                section["example"] = ""


    return lesson


# ============================================================
# VALIDACIÓN
# ============================================================

def validate_lesson_json(
    data: dict,
):

    if not isinstance(
        data,
        dict,
    ):

        raise ValueError(
            "La respuesta de la lección "
            "debe ser un objeto JSON"
        )


    # Solamente estos 3 son realmente
    # necesarios para renderizar la clase.

    required_fields = [
        "title",
        "introduction",
        "sections",
    ]


    for field in required_fields:

        if field not in data:

            raise ValueError(
                f"El LLM no devolvió "
                f"el campo obligatorio: {field}"
            )


    if not isinstance(
        data["title"],
        str,
    ):

        raise ValueError(
            "title debe ser texto"
        )


    if not isinstance(
        data["introduction"],
        str,
    ):

        raise ValueError(
            "introduction debe ser texto"
        )


    if not isinstance(
        data["sections"],
        list,
    ):

        raise ValueError(
            "sections debe ser una lista"
        )


    if not isinstance(
        data["key_points"],
        list,
    ):

        raise ValueError(
            "key_points debe ser una lista"
        )


    if len(
        data["sections"]
    ) == 0:

        raise ValueError(
            "La lección debe contener "
            "al menos una sección"
        )


    for index, section in enumerate(
        data["sections"]
    ):

        if not isinstance(
            section,
            dict,
        ):

            raise ValueError(
                f"Sección {index + 1} "
                f"debe ser un objeto"
            )


        if "title" not in section:

            raise ValueError(
                f"Sección {index + 1}: "
                f"falta title"
            )


        if "content" not in section:

            raise ValueError(
                f"Sección {index + 1}: "
                f"falta content"
            )


# ============================================================
# GENERAR LECCIÓN
# ============================================================

async def generate_lesson(
    topic: str,
    chunks: list[dict] | None = None,
    config: dict | None = None,
):

    # --------------------------------------------------------
    # 1. Configuración pedagógica
    # --------------------------------------------------------

    if config is None:

        config = LESSON_CONFIGS.get(
            topic
        )


    if config is None:

        raise ValueError(
            f"No existe configuración "
            f"pedagógica para {topic}"
        )


    # --------------------------------------------------------
    # 2. Contenido MongoDB
    # --------------------------------------------------------

    if chunks is None:

        chunks = await get_topic_chunks(
            topic
        )


    if not chunks:

        raise ValueError(
            f"No existe contenido en "
            f"MongoDB para {topic}"
        )


    # --------------------------------------------------------
    # 3. Contexto
    # --------------------------------------------------------

    context = build_context(
        chunks
    )


    # --------------------------------------------------------
    # 4. Enfoque pedagógico
    # --------------------------------------------------------

    lesson_focus = "\n".join(
        f"- {item}"
        for item in config[
            "lesson_focus"
        ]
    )


    # --------------------------------------------------------
    # 5. Prompt
    # --------------------------------------------------------

    prompt = f"""
{BASE_LESSON_PROMPT}


TEMA:

{topic} - {chunks[0]["title"]}


OBJETIVO DE APRENDIZAJE:

{config["learning_goal"]}


ESTRATEGIA PEDAGÓGICA:

{config["teaching_strategy"]}


ASPECTOS QUE DEBES PRIORIZAR:

{lesson_focus}


CONTEXTO DEL MANUAL OFICIAL:

{context}


Genera ahora la mini lección.


IMPORTANTE:

- utiliza solamente el contexto proporcionado
- no inventes información
- devuelve exclusivamente JSON válido

La raíz debe contener:

"title"
"introduction"
"sections"
"key_points"

Cada elemento de "sections" debe utilizar:

"title"
"content"
"example"

No utilices nombres alternativos como:

"section_title"
"heading"
"text"

No envuelvas la respuesta dentro de:

"lesson"
"data"
"result"
"""


    # --------------------------------------------------------
    # 6. LLM
    # --------------------------------------------------------

    response = await generate_text(
        prompt
    )


    # --------------------------------------------------------
    # 7. Limpiar JSON
    # --------------------------------------------------------

    cleaned_response = (
        clean_json_response(
            response
        )
    )


    # --------------------------------------------------------
    # 8. Parsear JSON
    # --------------------------------------------------------

    try:

        lesson = json.loads(
            cleaned_response
        )

    except json.JSONDecodeError as error:

        print(
            "\n"
            "ERROR: El LLM no devolvió "
            "JSON válido"
            "\n"
        )

        print(
            cleaned_response
        )

        raise ValueError(
            "El modelo no devolvió "
            "JSON válido"
        ) from error


    # --------------------------------------------------------
    # 9. Normalizar JSON
    # --------------------------------------------------------

    lesson = normalize_lesson_json(
        lesson
    )


    # --------------------------------------------------------
    # 10. Validar JSON
    # --------------------------------------------------------

    try:

        validate_lesson_json(
            lesson
        )

    except ValueError as error:

        print(
            "\n"
            "ERROR: JSON con estructura "
            "inválida"
            "\n"
        )

        print(
            json.dumps(
                lesson,
                ensure_ascii=False,
                indent=2,
            )
        )

        raise error


    # --------------------------------------------------------
    # 11. Fuentes
    # --------------------------------------------------------

    sources = []

    seen_pages = set()


    for chunk in chunks:

        page = chunk["page"]

        if page in seen_pages:
            continue


        seen_pages.add(
            page
        )


        sources.append(
            {
                "page": page,
                "title": chunk["title"],
                "source": chunk["source"],
            }
        )


    # --------------------------------------------------------
    # 12. Response
    # --------------------------------------------------------

    return {
        "topic": topic,
        "lesson": lesson,
        "sources": sources,
    }