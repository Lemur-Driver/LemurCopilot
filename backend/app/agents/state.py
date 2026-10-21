from typing import Any, Literal, TypedDict


class AgentState(TypedDict, total=False):
    topic: str
    learner_profile: dict[str, Any]
    strategy: Literal["reinforcement", "standard", "challenge"]
    lesson: dict[str, Any] | None
    exercises: list[dict[str, Any]]
    decision_reason: str
    errors: list[str]
    focus_concepts: list[str]
    focus_reason: str
    content_request: dict[str, Any]
    release_id: str | None
    lesson_variant: Literal["reinforcement", "standard", "challenge"] | None
    content_errors: list[str]
