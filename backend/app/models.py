from datetime import datetime
from typing import Annotated, Any, Literal

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class MongoBaseModel(BaseModel):
    """Base para todos los documentos: mapea _id de Mongo al campo id."""

    id: PyObjectId | None = Field(default=None, alias="_id")
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


# ---------- students ----------

class MasteryEntry(BaseModel):
    score: float = 0.0
    last_score: float = 0.0
    best_score: float = 0.0
    attempts: int = 0
    last_seen: datetime | None = None
    failed_questions: list[str] = Field(default_factory=list)


def get_mastery_entry(mastery: dict[str, Any], topic: str) -> MasteryEntry | None:
    value: Any = mastery
    for part in topic.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    if not isinstance(value, dict):
        return None
    return MasteryEntry.model_validate(value)


def flatten_mastery(mastery: dict[str, Any]) -> dict[str, MasteryEntry]:
    flattened: dict[str, MasteryEntry] = {}

    def visit(value: Any, prefix: str) -> None:
        if not isinstance(value, dict):
            return
        if any(field in value for field in MasteryEntry.model_fields):
            flattened[prefix] = MasteryEntry.model_validate(value)
            return
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            visit(child, child_prefix)

    visit(mastery, "")
    return flattened


class Student(MongoBaseModel):
    google_sub: str
    name: str
    email: str
    picture: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)
    current_unit: str | None = None
    mastery: dict[str, Any] = Field(default_factory=dict)


# ---------- concepts ----------

class Concept(MongoBaseModel):
    unit: str
    name: str
    description: str | None = None
    prerequisites: list[PyObjectId] = Field(default_factory=list)
    source_refs: list[PyObjectId] = Field(default_factory=list)


# ---------- exercises ----------

class Exercise(MongoBaseModel):
    topic: str | None = None
    language: str = "es"
    concept_id: PyObjectId | None = None
    concept_tags: list[str] = Field(default_factory=list)
    misconception_tags: list[str] = Field(default_factory=list)
    cognitive_skill: str | None = None
    type: Literal["multiple_choice", "true_false", "open"] = "multiple_choice"
    question: str
    options: list[str] = Field(default_factory=list)
    correct_answer: str | None = None
    correct_index: int | None = None
    explanation: str | None = None
    difficulty: float = 0.5
    generated_by: Literal["llm", "manual"] = "llm"
    source_chunk_ids: list[PyObjectId] = Field(default_factory=list)
    fingerprint: str | None = None
    content_version: str | None = None
    prompt_version: str | None = None
    verification_version: str | int | None = None
    release_id: str | None = None
    status: Literal[
        "pending", "generating", "generated", "verifying", "ready",
        "published", "rejected", "failed", "superseded",
    ] = "pending"
    verified: bool = False
    reviewed: bool = False
    review_status: Literal["pending", "approved", "rejected"] | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    times_served: int = 0
    times_correct: int = 0
    times_incorrect: int = 0


class GeneratedLesson(MongoBaseModel):
    topic: str
    variant: Literal["standard", "reinforcement", "challenge"]
    language: str = "es"
    lesson: dict[str, Any]
    concept_tags: list[str] = Field(default_factory=list)
    source_chunk_ids: list[PyObjectId] = Field(default_factory=list)
    content_version: str
    prompt_version: str
    verification_version: str
    release_id: str
    status: Literal[
        "pending", "generating", "generated", "verifying", "ready",
        "published", "rejected", "failed", "superseded",
    ] = "pending"
    verified: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    generation_metadata: dict[str, Any] = Field(default_factory=dict)


class ContentRelease(MongoBaseModel):
    release_id: str
    content_version: str
    status: Literal[
        "building", "validating", "ready", "published", "superseded", "failed",
    ] = "building"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: datetime | None = None
    topics: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContentJob(MongoBaseModel):
    job_id: str
    release_id: str
    topic: str
    job_type: str = "generate_topic"
    status: Literal[
        "pending", "generating", "generated", "verifying", "ready",
        "published", "rejected", "failed", "superseded",
    ] = "pending"
    attempts: int = 0
    error_type: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    generated_count: int = 0
    rejected_count: int = 0
    verification_failures: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------- sessions ----------

class SessionMessage(BaseModel):
    role: Literal["agent", "student"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExerciseAttempt(BaseModel):
    exercise_id: PyObjectId | None = None
    correct: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class QuizAnswerRecord(BaseModel):
    exercise_id: PyObjectId | None = None
    question: str
    selected_index: int
    correct_index: int | None = None
    is_correct: bool
    topic: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Session(MongoBaseModel):
    student_id: PyObjectId
    started_at: datetime = Field(default_factory=datetime.utcnow)
    quiz_topic: str | None = None
    quiz_exercise_ids: list[PyObjectId] = Field(default_factory=list)
    quiz_status: Literal["assigned", "completed"] | None = None
    completed_at: datetime | None = None
    score: float | None = None
    answers: list[QuizAnswerRecord] = Field(default_factory=list)
    messages: list[SessionMessage] = Field(default_factory=list)
    exercises_attempted: list[ExerciseAttempt] = Field(default_factory=list)


# ---------- content_chunks (RAG) ----------

class ContentChunk(MongoBaseModel):
    topic: str | None = None
    title: str
    page: int | None = None
    chunk_index: int | None = None
    text: str
    embedding: list[float]