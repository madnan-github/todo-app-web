"""Unit tests for Task model validation (T005).

TDD: These tests must FAIL before implementation.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models.task import Task


class TestTaskCreation:
    """Tests for basic Task model creation."""

    def test_create_task_with_valid_data(self) -> None:
        """Task can be created with valid id, title, and description."""
        task = Task(id=1, title="Buy groceries", description="Milk, eggs, bread")
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False

    def test_create_task_with_minimal_data(self) -> None:
        """Task can be created with only required fields (id and title)."""
        task = Task(id=1, title="Simple task")
        assert task.id == 1
        assert task.title == "Simple task"
        assert task.description == ""
        assert task.completed is False

    def test_create_task_has_timestamps(self) -> None:
        """Task automatically gets created_at and updated_at timestamps."""
        task = Task(id=1, title="Test task")
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_create_task_with_explicit_completed_status(self) -> None:
        """Task can be created with explicit completed status."""
        task = Task(id=1, title="Completed task", completed=True)
        assert task.completed is True


class TestTaskIdValidation:
    """Tests for Task ID validation (FR-003, FR-015)."""

    def test_id_must_be_positive(self) -> None:
        """Task ID must be >= 1."""
        with pytest.raises(ValidationError) as exc_info:
            Task(id=0, title="Invalid task")
        assert "greater than or equal to 1" in str(exc_info.value).lower()

    def test_id_negative_not_allowed(self) -> None:
        """Negative task ID is not allowed."""
        with pytest.raises(ValidationError):
            Task(id=-1, title="Invalid task")

    def test_id_valid_minimum(self) -> None:
        """Task ID of 1 is valid (minimum)."""
        task = Task(id=1, title="Valid task")
        assert task.id == 1

    def test_id_large_value_allowed(self) -> None:
        """Large task ID values are allowed."""
        task = Task(id=999999, title="Large ID task")
        assert task.id == 999999


class TestTaskTitleValidation:
    """Tests for Task title validation (FR-002, FR-008)."""

    def test_title_required(self) -> None:
        """Task must have a title."""
        with pytest.raises(ValidationError):
            Task(id=1)  # Missing title

    def test_title_cannot_be_empty(self) -> None:
        """Title cannot be an empty string."""
        with pytest.raises(ValidationError):
            Task(id=1, title="")

    def test_title_cannot_be_whitespace_only(self) -> None:
        """Title cannot be whitespace only."""
        with pytest.raises(ValidationError):
            Task(id=1, title="   ")

    def test_title_whitespace_is_stripped(self) -> None:
        """Leading and trailing whitespace in title is stripped."""
        task = Task(id=1, title="  Buy groceries  ")
        assert task.title == "Buy groceries"

    def test_title_max_length_200_chars(self) -> None:
        """Title cannot exceed 200 characters."""
        long_title = "a" * 201
        with pytest.raises(ValidationError):
            Task(id=1, title=long_title)

    def test_title_exactly_200_chars_allowed(self) -> None:
        """Title of exactly 200 characters is allowed."""
        title_200 = "a" * 200
        task = Task(id=1, title=title_200)
        assert len(task.title) == 200

    def test_title_single_character_valid(self) -> None:
        """Single character title is valid."""
        task = Task(id=1, title="X")
        assert task.title == "X"


class TestTaskDescriptionValidation:
    """Tests for Task description validation (FR-002, FR-008)."""

    def test_description_optional(self) -> None:
        """Description is optional (defaults to empty string)."""
        task = Task(id=1, title="Test task")
        assert task.description == ""

    def test_description_max_length_1000_chars(self) -> None:
        """Description cannot exceed 1000 characters."""
        long_desc = "a" * 1001
        with pytest.raises(ValidationError):
            Task(id=1, title="Test", description=long_desc)

    def test_description_exactly_1000_chars_allowed(self) -> None:
        """Description of exactly 1000 characters is allowed."""
        desc_1000 = "a" * 1000
        task = Task(id=1, title="Test", description=desc_1000)
        assert len(task.description) == 1000

    def test_description_whitespace_is_stripped(self) -> None:
        """Leading and trailing whitespace in description is stripped."""
        task = Task(id=1, title="Test", description="  Some details  ")
        assert task.description == "Some details"

    def test_description_empty_string_allowed(self) -> None:
        """Empty string description is allowed."""
        task = Task(id=1, title="Test", description="")
        assert task.description == ""


class TestTaskCompletedStatus:
    """Tests for Task completed status field."""

    def test_completed_defaults_to_false(self) -> None:
        """New tasks default to incomplete (completed=False)."""
        task = Task(id=1, title="New task")
        assert task.completed is False

    def test_completed_can_be_true(self) -> None:
        """Task can be created with completed=True."""
        task = Task(id=1, title="Done task", completed=True)
        assert task.completed is True

    def test_completed_is_boolean(self) -> None:
        """Completed field is a boolean."""
        task = Task(id=1, title="Test")
        assert isinstance(task.completed, bool)


class TestTaskTimestamps:
    """Tests for Task timestamp fields."""

    def test_created_at_auto_generated(self) -> None:
        """created_at is automatically set to current time."""
        before = datetime.now()
        task = Task(id=1, title="Test task")
        after = datetime.now()
        assert before <= task.created_at <= after

    def test_updated_at_auto_generated(self) -> None:
        """updated_at is automatically set to current time."""
        before = datetime.now()
        task = Task(id=1, title="Test task")
        after = datetime.now()
        assert before <= task.updated_at <= after

    def test_timestamps_can_be_explicit(self) -> None:
        """Timestamps can be provided explicitly."""
        specific_time = datetime(2025, 1, 1, 12, 0, 0)
        task = Task(
            id=1,
            title="Test",
            created_at=specific_time,
            updated_at=specific_time,
        )
        assert task.created_at == specific_time
        assert task.updated_at == specific_time
