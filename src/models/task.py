"""Task Pydantic model with validation (T007).

This module defines the Task entity for the todo application.
Validation rules per data-model.md specification.
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    """Represents a todo task with validation.

    Attributes:
        id: Unique task identifier (>= 1)
        title: Task title (1-200 chars, required)
        description: Optional task description (max 1000 chars)
        completed: Task completion status (default: False)
        created_at: Task creation timestamp (auto-generated)
        updated_at: Last update timestamp (auto-generated)
    """

    id: int = Field(ge=1, description="Unique task identifier")
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required)",
    )
    description: str = Field(
        default="",
        max_length=1000,
        description="Optional task description",
    )
    completed: bool = Field(
        default=False,
        description="Task completion status",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Task creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp",
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_strip(cls, v: str) -> str:
        """Strip whitespace from description."""
        return v.strip() if v else ""
