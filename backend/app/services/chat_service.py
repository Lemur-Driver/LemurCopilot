import json

from app.prompts.chat_prompts import (
    CHAT_SYSTEM_PROMPT,
    DOMAIN_CLASSIFIER_PROMPT,
)

from app.services.llm_service import (
    generate_text,
)


# ============================================================
# CONSTANTES
# ============================================================

IN_DOMAIN = "IN_DOMAIN"
OUT_OF_DOMAIN = "OUT_OF_DOMAIN"


OUT_OF_DOMAIN_RESPONSE = (
    "Estoy especializado en conducción y seguridad vial 🚗. "
    "Puedo ayudarte con temas relacionados con la licencia Clase B, "
    "normas de tránsito, seguridad vial o funcionamiento del vehículo."
)


# ============================================================
# CONSTRUIR HISTORIAL
# ============================================================

def build_history_text(
    history: list[dict],
) -> str:

    parts = []


    for message in history:

        role = message.get(
            "role"
        )

        content = message.get(
            "content",
            "",
        )


        if role == "user":

            parts.append(
                f"Usuario: {content}"
            )


        elif role == "assistant":

            parts.append(
                f"Asistente: {content}"
            )


    if not parts:

        return "(sin historial)"


    return "\n\n".join(
        parts
    )


# ============================================================
# CLASIFICADOR DE DOMINIO
# ============================================================

async def classify_domain(
    message: str,
    history: list[dict],
) -> str:

    history_text = build_history_text(
        history
    )


    classifier_prompt = f"""
{DOMAIN_CLASSIFIER_PROMPT}


HISTORIAL DE CONVERSACIÓN:

{history_text}


MENSAJE ACTUAL:

{message}


Clasifica ahora el mensaje.
"""


    # Aquí SÍ queremos JSON.
    response = await generate_text(
        prompt=classifier_prompt,
        json_mode=True,
    )


    try:

        data = json.loads(
            response.strip()
        )


        classification = data.get(
            "classification"
        )


        if classification in {
            IN_DOMAIN,
            OUT_OF_DOMAIN,
        }:

            return classification


    except json.JSONDecodeError:

        print(
            "\n"
            "ERROR: El clasificador no "
            "devolvió JSON válido"
            "\n"
        )

        print(
            response
        )


    # --------------------------------------------------------
    # FALLBACK SEGURO
    # --------------------------------------------------------
    #
    # Si el clasificador falla,
    # preferimos NO mandar la consulta al tutor.
    # --------------------------------------------------------

    return OUT_OF_DOMAIN


# ============================================================
# CONSTRUIR PROMPT DEL TUTOR
# ============================================================

def build_chat_prompt(
    history: list[dict],
    current_message: str,
) -> str:

    history_text = build_history_text(
        history
    )


    return f"""
{CHAT_SYSTEM_PROMPT}


============================================================
HISTORIAL DE CONVERSACIÓN
============================================================

{history_text}


============================================================
MENSAJE ACTUAL DEL USUARIO
============================================================

{current_message}


============================================================
INSTRUCCIÓN
============================================================

Responde al mensaje actual teniendo en cuenta
el historial cuando sea necesario.

Mantén siempre tu rol de tutor de conducción.
"""


# ============================================================
# GENERAR RESPUESTA
# ============================================================

async def generate_chat_response(
    message: str,
    history: list[dict],
) -> str:

    # --------------------------------------------------------
    # 1. Guardrail de dominio
    # --------------------------------------------------------

    classification = await classify_domain(
        message=message,
        history=history,
    )


    print(
        f"\nCHAT DOMAIN: {classification}"
    )


    # --------------------------------------------------------
    # 2. Fuera de dominio
    # --------------------------------------------------------

    if classification == OUT_OF_DOMAIN:

        return OUT_OF_DOMAIN_RESPONSE


    # --------------------------------------------------------
    # 3. Construir prompt tutor
    # --------------------------------------------------------

    prompt = build_chat_prompt(
        history=history,
        current_message=message,
    )


    # --------------------------------------------------------
    # 4. Generar respuesta
    # --------------------------------------------------------
    #
    # Aquí queremos lenguaje natural,
    # NO JSON.
    # --------------------------------------------------------

    response = await generate_text(
        prompt=prompt,
        json_mode=False,
    )


    return response.strip()