from uuid import UUID
from typing import Any

from pydantic import BaseModel, Field


class Module2Input(BaseModel):

    student_id: UUID

    relevant_memories: list[dict[str, Any]] = Field(
        default_factory=list
    )

    weekly_update_summary: dict[str, Any] | None = None

    weekly_new_information: list[Any] = Field(default_factory=list)

    weekly_changes: list[dict[str, Any]] = Field(
        default_factory=list
    )

    trigger: str | None = None

    trigger_reasons: list[str] = Field(
        default_factory=list
    )