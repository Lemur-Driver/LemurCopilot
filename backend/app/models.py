from datetime import datetime
from typing import Annotated, Literal

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
    attempts: int = 0
    last_seen: datetime | None = None


class Student(MongoBaseModel):
    name: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    current_unit: str | None = None
    mastery: dict[str, MasteryEntry] = Field(default_factory=dict)


# ---------- concepts ----------

class Concept(MongoBaseModel):
    unit: str
    name: str
    description: str | None = None
    prerequisites: list[PyObjectId] = Field(default_factory=list)
    source_refs: list[PyObjectId] = Field(default_factory=list)


# ---------- exercises ----------

class Exercise(MongoBaseModel):
    concept_id: PyObjectId
    type: Literal["multiple_choice", "true_false", "open"] = "multiple_choice"
    question: str
    options: list[str] = Field(default_factory=list)
    correct_answer: str
    difficulty: float = 0.5
    generated_by: Literal["llm", "manual"] = "llm"
    source_chunk_ids: list[PyObjectId] = Field(default_factory=list) 
    reviewed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    times_served: int = 0
    times_correct: int = 0
    times_incorrect: int = 0


# ---------- sessions ----------

class SessionMessage(BaseModel):
    role: Literal["agent", "student"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExerciseAttempt(BaseModel):
    exercise_id: PyObjectId
    correct: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Session(MongoBaseModel):
    student_id: PyObjectId
    started_at: datetime = Field(default_factory=datetime.utcnow)
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
