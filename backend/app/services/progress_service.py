from app.models import Student, get_mastery_entry


# ============================================================
# CONFIG
# ============================================================

PASSING_SCORE = 0.6


# ============================================================
# ESTRUCTURA DEL CURSO
# ============================================================

COURSE_UNITS = [
    {
        "id": "unit-1",
        "lessons": [
            "C1",
            "C1.1",
            "C1.2",
        ],
    },
    {
        "id": "unit-2",
        "lessons": [
            "C2.1",
            "C2.2",
            "C2.3",
        ],
    },
    {
        "id": "unit-3",
        "lessons": [
            "C3",
        ],
    },
    {
        "id": "unit-4",
        "lessons": [
            "C4",
            "C4.1",
            "C4.2",
            "C4.3",
            "C4.4",
            "C4.5",
            "C4.6",
            "C4.7",
        ],
    },
    {
        "id": "unit-5",
        "lessons": [
            "C5",
            "C5.1",
        ],
    },
    {
        "id": "unit-6",
        "lessons": [
            "C6",
            "C6.1",
            "C6.2",
            "C6.3",
            "C6.4",
            "C6.5",
            "C6.6",
        ],
    },
    {
        "id": "unit-7",
        "lessons": [
            "C7.1",
            "C7.2",
            "C7.3",
            "C7.4",
        ],
    },
    {
        "id": "unit-8",
        "lessons": [
            "C8.1",
            "C8.2",
            "C8.3",
        ],
    },
    {
        "id": "unit-9",
        "lessons": [
            "C9.1",
            "C9.2",
            "C9.3",
            "C9.4",
            "C9.5",
            "C9.6",
        ],
    },
]


ANNEX_TOPICS = {
    "A1",
    "A2.1",
    "A2.2",
    "A3",
}


# ============================================================
# COMPLETAR LECCIÓN
# ============================================================

def is_lesson_completed(
    student: Student,
    topic: str,
) -> bool:

    mastery = get_mastery_entry(
        student.mastery,
        topic,
    )

    if mastery is None:
        return False

    return mastery.best_score >= PASSING_SCORE


# ============================================================
# COMPLETAR UNIDAD
# ============================================================

def is_unit_completed(
    student: Student,
    unit_index: int,
) -> bool:

    if (
        unit_index < 0
        or unit_index >= len(COURSE_UNITS)
    ):
        return False

    lessons = COURSE_UNITS[
        unit_index
    ]["lessons"]

    return all(
        is_lesson_completed(
            student,
            topic,
        )
        for topic in lessons
    )


# ============================================================
# UNIDAD DESBLOQUEADA
# ============================================================

def is_unit_unlocked(
    student: Student,
    unit_index: int,
) -> bool:

    # Unidad 1 siempre disponible.
    if unit_index == 0:
        return True

    if (
        unit_index < 0
        or unit_index >= len(COURSE_UNITS)
    ):
        return False

    # Para llegar a una unidad,
    # todas las anteriores deben estar completas.
    return all(
        is_unit_completed(
            student,
            previous_index,
        )
        for previous_index
        in range(unit_index)
    )


# ============================================================
# TOPIC DESBLOQUEADO
# ============================================================

def is_topic_unlocked(
    student: Student,
    topic: str,
) -> bool:

    # Los anexos son material complementario.
    if topic in ANNEX_TOPICS:
        return True

    for unit_index, unit in enumerate(
        COURSE_UNITS
    ):

        if topic in unit["lessons"]:

            return is_unit_unlocked(
                student,
                unit_index,
            )

    # Si el topic ni siquiera pertenece al curso,
    # no se permite.
    return False


# ============================================================
# ESTADO COMPLETO DEL CURSO PARA FRONTEND
# ============================================================

def build_course_progress(
    student: Student,
) -> list[dict]:

    progress = []

    for unit_index, unit in enumerate(
        COURSE_UNITS
    ):

        completed_lessons = sum(
            1
            for topic in unit["lessons"]
            if is_lesson_completed(
                student,
                topic,
            )
        )

        total_lessons = len(
            unit["lessons"]
        )

        progress.append(
            {
                "unit_id": unit["id"],
                "unlocked": is_unit_unlocked(
                    student,
                    unit_index,
                ),
                "completed": (
                    completed_lessons
                    == total_lessons
                ),
                "completed_lessons":
                    completed_lessons,
                "total_lessons":
                    total_lessons,
            }
        )

    # Anexos libres.
    progress.append(
        {
            "unit_id": "unit-annexes",
            "unlocked": True,
            "completed": False,
            "completed_lessons": 0,
            "total_lessons": len(
                ANNEX_TOPICS
            ),
        }
    )

    return progress