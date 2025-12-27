# Data Model: Console Todo CRUD Application

**Feature**: 001-console-todo-crud | **Date**: 2025-12-27

## Overview

This document defines the data model for the Phase I Console Todo CRUD application. The model is designed for in-memory storage with future migration to SQLModel/PostgreSQL in Phase II.

---

## Entities

### Task

The primary entity representing a todo item.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | Auto-generated, unique | Unique identifier |
| `title` | `str` | Required, 1-200 chars | Task title |
| `description` | `str` | Optional, max 1000 chars | Detailed description |
| `completed` | `bool` | Default: False | Completion status |
| `created_at` | `datetime` | Auto-generated | Creation timestamp |
| `updated_at` | `datetime` | Auto-generated | Last modification timestamp |

**Pydantic Model Definition**:

```python
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class Task(BaseModel):
    """Represents a todo task with validation."""

    id: int = Field(ge=1, description="Unique task identifier")
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required)"
    )
    description: str = Field(
        default="",
        max_length=1000,
        description="Optional task description"
    )
    completed: bool = Field(
        default=False,
        description="Task completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_strip(cls, v: str) -> str:
        """Strip whitespace from description."""
        return v.strip() if v else ""
```

---

## Validation Rules

### Title Validation (FR-002, FR-008)

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Required | Cannot be None | "Title is required" |
| Not Empty | Min 1 char after stripping | "Title cannot be empty or whitespace only" |
| Max Length | Max 200 characters | "Title must be 200 characters or less" |
| Whitespace | Leading/trailing trimmed | N/A (auto-trimmed) |

### Description Validation (FR-002, FR-008)

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Optional | Can be empty string | N/A |
| Max Length | Max 1000 characters | "Description must be 1000 characters or less" |
| Whitespace | Leading/trailing trimmed | N/A (auto-trimmed) |

### ID Validation (FR-003, FR-015)

| Rule | Constraint | Error Message |
|------|------------|---------------|
| Positive | Must be >= 1 | "Invalid task ID" |
| Exists | Must exist in storage | "Task not found" |
| Format | Must be integer | "Task ID must be a number" |

---

## State Transitions

### Task Completion Status

```
┌──────────┐                    ┌───────────┐
│ pending  │ ──mark complete──► │ completed │
│(default) │                    │           │
└──────────┘                    └───────────┘
```

**Transition Rules**:
- New tasks start as `pending` (completed=False)
- `Mark Complete` action sets `completed=True`
- Attempting to mark an already completed task shows info message (FR-014, US-3.2)
- No transition back to pending in Phase I (out of scope)

---

## Data Transfer Objects

### TaskCreate (Input for Add)

```python
class TaskCreate(BaseModel):
    """Input model for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
```

### TaskUpdate (Input for Update)

```python
class TaskUpdate(BaseModel):
    """Input model for updating a task. All fields optional."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
```

---

## Storage Operations

### InMemoryStorage Interface

```python
class InMemoryStorage:
    """In-memory task storage with CRUD operations."""

    def add(self, title: str, description: str = "") -> Task:
        """Create a new task with auto-generated ID and timestamps."""

    def get(self, task_id: int) -> Task | None:
        """Get a task by ID. Returns None if not found."""

    def get_all(self) -> list[Task]:
        """Get all tasks, ordered by creation date (newest first)."""

    def update(self, task_id: int, title: str | None = None,
               description: str | None = None) -> Task | None:
        """Update task fields. Returns None if task not found."""

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Returns True if deleted, False if not found."""

    def mark_complete(self, task_id: int) -> Task | None:
        """Mark a task as complete. Returns None if not found."""
```

---

## Error Handling

### Validation Errors

| Error Type | Trigger | User Message |
|------------|---------|--------------|
| `EmptyTitleError` | Title is empty/whitespace | "Error: Title cannot be empty" |
| `TitleTooLongError` | Title > 200 chars | "Error: Title must be 200 characters or less" |
| `DescriptionTooLongError` | Description > 1000 chars | "Error: Description must be 1000 characters or less" |
| `InvalidIdError` | ID not a number | "Error: Please enter a valid task ID (number)" |
| `TaskNotFoundError` | ID doesn't exist | "Error: Task #{id} not found" |

---

## Display Formatting

### Task List Table (FR-007)

| Column | Field | Format |
|--------|-------|--------|
| ID | `id` | Right-aligned integer |
| Title | `title` | Left-aligned, truncated at 40 chars |
| Status | `completed` | "✓" (green) or "○" (dim) |
| Created | `created_at` | "YYYY-MM-DD HH:MM" |

**Example Output**:
```
┌────┬────────────────────────────────────────┬────────┬──────────────────┐
│ ID │ Title                                  │ Status │ Created          │
├────┼────────────────────────────────────────┼────────┼──────────────────┤
│  1 │ Buy groceries                          │   ○    │ 2025-12-27 10:30 │
│  2 │ Complete Phase I implementation        │   ✓    │ 2025-12-27 11:00 │
│  3 │ Review pull request                    │   ○    │ 2025-12-27 11:30 │
└────┴────────────────────────────────────────┴────────┴──────────────────┘
```

---

## Phase II Migration Notes

When migrating to SQLModel/PostgreSQL in Phase II:

1. **Task model** → Add `Table=True` to make it a SQLModel table
2. **Storage** → Replace InMemoryStorage with SQLModel session
3. **ID** → Change to database auto-increment primary key
4. **Timestamps** → Add database default constraints
5. **User ID** → Add foreign key relationship (multi-user support)

```python
# Phase II SQLModel version
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")  # New in Phase II
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```
