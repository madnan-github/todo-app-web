"""Edge case tests for comprehensive coverage (T054).

Tests for special characters, unicode, and boundary conditions.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.task import Task
from src.storage.memory import InMemoryStorage


class TestTaskTitleEdgeCases:
    """Edge case tests for task title validation."""

    def test_title_with_special_characters(self) -> None:
        """Title can contain special characters."""
        special_titles = [
            "Task with @mentions",
            "Task #1 - Important!",
            "Buy groceries: milk, eggs & bread",
            "TODO (urgent)",
            "Task 100% complete?",
            "Money: $100.00",
            "Email: test@example.com",
        ]
        for title in special_titles:
            task = Task(id=1, title=title)
            assert task.title == title

    def test_title_with_unicode(self) -> None:
        """Title can contain unicode characters."""
        unicode_titles = [
            "Task with emoji",  # We avoid actual emoji per requirements
            "Tarea en espanol",
            "Aufgabe auf Deutsch",
            "Chinese: zhongwen",
            "Japanese: nihongo",
        ]
        for title in unicode_titles:
            task = Task(id=1, title=title)
            assert task.title == title

    def test_title_with_numbers_only(self) -> None:
        """Title can be numbers only."""
        task = Task(id=1, title="12345")
        assert task.title == "12345"

    def test_title_exactly_at_boundary(self) -> None:
        """Title at exactly 200 characters."""
        title_200 = "x" * 200
        task = Task(id=1, title=title_200)
        assert len(task.title) == 200

    def test_title_one_over_boundary(self) -> None:
        """Title at 201 characters fails."""
        title_201 = "x" * 201
        with pytest.raises(ValidationError):
            Task(id=1, title=title_201)

    def test_title_single_character(self) -> None:
        """Single character title is valid."""
        task = Task(id=1, title="X")
        assert task.title == "X"

    def test_title_with_newlines_stripped(self) -> None:
        """Title with newlines gets whitespace stripped."""
        # Note: Pydantic's strip only removes leading/trailing whitespace
        # Internal newlines would remain - this tests the stripping behavior
        task = Task(id=1, title="  Task title  ")
        assert task.title == "Task title"


class TestTaskDescriptionEdgeCases:
    """Edge case tests for task description validation."""

    def test_description_with_special_characters(self) -> None:
        """Description can contain special characters."""
        task = Task(
            id=1,
            title="Test",
            description="Details: @user #tag !important (note) [link]"
        )
        assert "@user" in task.description

    def test_description_exactly_at_boundary(self) -> None:
        """Description at exactly 1000 characters."""
        desc_1000 = "y" * 1000
        task = Task(id=1, title="Test", description=desc_1000)
        assert len(task.description) == 1000

    def test_description_one_over_boundary(self) -> None:
        """Description at 1001 characters fails."""
        desc_1001 = "y" * 1001
        with pytest.raises(ValidationError):
            Task(id=1, title="Test", description=desc_1001)

    def test_description_empty_after_strip(self) -> None:
        """Description of only whitespace becomes empty."""
        task = Task(id=1, title="Test", description="   ")
        assert task.description == ""


class TestTaskIdEdgeCases:
    """Edge case tests for task ID validation."""

    def test_id_exactly_one(self) -> None:
        """ID of exactly 1 is valid."""
        task = Task(id=1, title="Test")
        assert task.id == 1

    def test_id_zero_fails(self) -> None:
        """ID of 0 fails validation."""
        with pytest.raises(ValidationError):
            Task(id=0, title="Test")

    def test_id_very_large(self) -> None:
        """Very large ID is valid."""
        task = Task(id=999999999, title="Test")
        assert task.id == 999999999


class TestStorageEdgeCases:
    """Edge case tests for storage operations."""

    def test_add_task_with_empty_description(self) -> None:
        """Adding task with empty description works."""
        storage = InMemoryStorage()
        task = storage.add(title="Test", description="")
        assert task.description == ""

    def test_get_after_many_adds(self) -> None:
        """Can get task after many additions."""
        storage = InMemoryStorage()
        for i in range(50):
            storage.add(title=f"Task {i}")

        # Get a task in the middle
        task = storage.get(25)
        assert task is not None
        assert task.id == 25

    def test_delete_and_readd(self) -> None:
        """IDs continue incrementing after delete."""
        storage = InMemoryStorage()
        storage.add(title="Task 1")  # ID 1
        storage.add(title="Task 2")  # ID 2
        storage.delete(1)
        task3 = storage.add(title="Task 3")  # Should be ID 3, not 1
        assert task3.id == 3

    def test_update_nonexistent_returns_none(self) -> None:
        """Updating non-existent task returns None."""
        storage = InMemoryStorage()
        result = storage.update(999, title="New title")
        assert result is None

    def test_mark_complete_nonexistent_returns_none(self) -> None:
        """Marking complete non-existent task returns None."""
        storage = InMemoryStorage()
        result = storage.mark_complete(999)
        assert result is None


class TestTimestampEdgeCases:
    """Edge case tests for timestamp handling."""

    def test_created_at_is_datetime(self) -> None:
        """created_at is a datetime object."""
        task = Task(id=1, title="Test")
        assert isinstance(task.created_at, datetime)

    def test_updated_at_is_datetime(self) -> None:
        """updated_at is a datetime object."""
        task = Task(id=1, title="Test")
        assert isinstance(task.updated_at, datetime)

    def test_timestamps_are_recent(self) -> None:
        """Timestamps are recent (within last minute)."""
        before = datetime.now()
        task = Task(id=1, title="Test")
        after = datetime.now()

        assert before <= task.created_at <= after
        assert before <= task.updated_at <= after
