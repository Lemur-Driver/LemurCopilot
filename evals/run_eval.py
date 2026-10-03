import csv
import json
import time

from pathlib import Path

import requests


# ============================================================
# CONFIG
# ============================================================

API_URL = (
    "http://localhost:8000/chat/stream"
)

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "dataset.csv"
)

RESULTS_DIR = (
    BASE_DIR
    / "results"
)

OUTPUT_PATH = (
    RESULTS_DIR
    / "prompt_v4.csv"
)

REQUEST_TIMEOUT = 180


# ============================================================
# CONSULTAR CHATBOT STREAMING
# ============================================================

def ask_chatbot(
    question: str,
) -> dict:

    payload = {
        "message":
            question,

        # Cada pregunta del baseline
        # es independiente.
        "history":
            [],
    }


    start_time = (
        time.perf_counter()
    )


    # --------------------------------------------------------
    # IMPORTANTE:
    #
    # stream=True evita que requests espere
    # el cuerpo completo antes de procesarlo.
    # --------------------------------------------------------

    response = requests.post(
        API_URL,
        json=payload,
        timeout=REQUEST_TIMEOUT,
        stream=True,
    )


    # --------------------------------------------------------
    # ERROR HTTP
    # --------------------------------------------------------

    if not response.ok:

        elapsed_time = (
            time.perf_counter()
            - start_time
        )


        return {
            "answer":
                "",

            "sources":
                [],

            "response_time_seconds":
                round(
                    elapsed_time,
                    3,
                ),

            "http_status":
                response.status_code,

            "error":
                response.text,
        }


    # ========================================================
    # RECONSTRUIR RESPUESTA DEL STREAM
    # ========================================================

    answer_parts = []

    sources = []

    stream_error = ""


    try:

        for line in response.iter_lines(
            decode_unicode=True
        ):

            if not line:
                continue


            try:

                event = json.loads(
                    line
                )

            except json.JSONDecodeError:

                print(
                    "⚠ Evento NDJSON inválido:"
                )

                print(
                    line
                )

                continue


            event_type = (
                event.get(
                    "type"
                )
            )


            # =================================================
            # SOURCES
            # =================================================

            if event_type == "sources":

                sources = event.get(
                    "sources",
                    [],
                )


            # =================================================
            # TOKEN
            # =================================================

            elif event_type == "token":

                content = event.get(
                    "content",
                    "",
                )


                if content:

                    answer_parts.append(
                        content
                    )


            # =================================================
            # ERROR DEL BACKEND
            # =================================================

            elif event_type == "error":

                stream_error = (
                    event.get(
                        "message",
                        "Error desconocido durante el stream",
                    )
                )


                break


            # =================================================
            # FIN
            # =================================================

            elif event_type == "done":

                break


    finally:

        response.close()


    elapsed_time = (
        time.perf_counter()
        - start_time
    )


    answer = "".join(
        answer_parts
    ).strip()


    return {
        "answer":
            answer,

        "sources":
            sources,

        "response_time_seconds":
            round(
                elapsed_time,
                3,
            ),

        "http_status":
            response.status_code,

        "error":
            stream_error,
    }


# ============================================================
# LEER DATASET
# ============================================================

def load_dataset() -> list[dict]:

    with DATASET_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )


        return list(
            reader
        )


# ============================================================
# GUARDAR RESULTADOS
# ============================================================

def save_results(
    results: list[dict],
):

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    if not results:
        return


    fieldnames = [
        "id",
        "category",
        "question",
        "expected_domain",
        "reference_pages",
        "reference_answer",
        "qwen_answer",
        "qwen_sources",
        "response_time_seconds",
        "http_status",
        "error",
    ]


    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )


        writer.writeheader()


        writer.writerows(
            results
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "========================================"
    )

    print(
        "LEMURCOPILOT - BASELINE EVALUATION"
    )

    print(
        "========================================"
    )

    print()


    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    if not DATASET_PATH.exists():

        print(
            "❌ No existe:"
        )

        print(
            DATASET_PATH
        )

        return


    dataset = load_dataset()


    if not dataset:

        print(
            "❌ El dataset está vacío."
        )

        return


    print(
        f"Preguntas: {len(dataset)}"
    )

    print(
        f"Endpoint: {API_URL}"
    )

    print()


    results = []


    # ========================================================
    # EVALUACIÓN
    # ========================================================

    for index, row in enumerate(
        dataset,
        start=1,
    ):

        question = (
            row
            .get(
                "question",
                "",
            )
            .strip()
        )


        print(
            f"[{index}/{len(dataset)}]"
        )

        print(
            question
        )


        # ----------------------------------------------------
        # PREGUNTA VACÍA
        # ----------------------------------------------------

        if not question:

            result = {
                "answer":
                    "",

                "sources":
                    [],

                "response_time_seconds":
                    "",

                "http_status":
                    "",

                "error":
                    "Pregunta vacía",
            }


        # ----------------------------------------------------
        # CONSULTA
        # ----------------------------------------------------

        else:

            try:

                result = ask_chatbot(
                    question
                )


            except requests.exceptions.Timeout:

                result = {
                    "answer":
                        "",

                    "sources":
                        [],

                    "response_time_seconds":
                        REQUEST_TIMEOUT,

                    "http_status":
                        "",

                    "error":
                        "Timeout",
                }


            except Exception as error:

                result = {
                    "answer":
                        "",

                    "sources":
                        [],

                    "response_time_seconds":
                        "",

                    "http_status":
                        "",

                    "error":
                        repr(
                            error
                        ),
                }


        # ====================================================
        # GUARDAR FILA
        # ====================================================

        output_row = {

            "id":
                row.get(
                    "id",
                    "",
                ),

            "category":
                row.get(
                    "category",
                    "",
                ),

            "question":
                question,

            "expected_domain":
                row.get(
                    "expected_domain",
                    "",
                ),

            "reference_pages":
                row.get(
                    "reference_pages",
                    "",
                ),

            "reference_answer":
                row.get(
                    "reference_answer",
                    "",
                ),

            "qwen_answer":
                result[
                    "answer"
                ],

            "qwen_sources":
                json.dumps(
                    result[
                        "sources"
                    ],
                    ensure_ascii=False,
                ),

            "response_time_seconds":
                result[
                    "response_time_seconds"
                ],

            "http_status":
                result[
                    "http_status"
                ],

            "error":
                result[
                    "error"
                ],
        }


        results.append(
            output_row
        )


        # ====================================================
        # CONSOLA
        # ====================================================

        if result["error"]:

            print(
                "❌ ERROR:"
            )

            print(
                result["error"]
            )


        else:

            print(
                f"✅ OK "
                f"({result['response_time_seconds']} s)"
            )


            print(
                "Qwen:"
            )


            answer_preview = (
                result[
                    "answer"
                ][:250]
            )


            print(
                answer_preview
            )


            if (
                len(
                    result[
                        "answer"
                    ]
                )
                > 250
            ):

                print(
                    "..."
                )


            print(
                f"Fuentes recuperadas: "
                f"{len(result['sources'])}"
            )


        print(
            "-" * 70
        )


        # ====================================================
        # GUARDADO INCREMENTAL
        # ====================================================
        #
        # Guardamos después de CADA pregunta.
        #
        # Si Qwen explota en la 49,
        # conservamos las primeras 48.
        # ====================================================

        save_results(
            results
        )


    # ========================================================
    # RESUMEN
    # ========================================================

    successes = [
        result

        for result in results

        if not result[
            "error"
        ]
    ]


    errors = (
        len(results)
        - len(successes)
    )


    times = [
        result[
            "response_time_seconds"
        ]

        for result in successes

        if isinstance(
            result[
                "response_time_seconds"
            ],
            (int, float),
        )
    ]


    average_time = (
        sum(times)
        / len(times)

        if times

        else 0
    )


    print()
    print(
        "========================================"
    )

    print(
        "EVALUACIÓN TERMINADA"
    )

    print(
        "========================================"
    )

    print(
        f"Total: {len(results)}"
    )

    print(
        f"OK: {len(successes)}"
    )

    print(
        f"Errores: {errors}"
    )

    print(
        f"Tiempo promedio: "
        f"{average_time:.2f} s"
    )

    print()

    print(
        "Resultado:"
    )

    print(
        OUTPUT_PATH
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()