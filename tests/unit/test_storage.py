"""Unit tests for InMemoryStorage CRUD operations (T006).

TDD: These tests must FAIL before implementation.
"""

from datetime import datetime

import pytest

from src.models.task import Task
from src.storage.memory import InMemoryStorage


class TestStorageAdd:
    """Tests for InMemoryStorage.add() method."""

    def test_add_task_returns_task_with_id(self) -> None:
        """Adding a task returns a Task with auto-generated ID."""
        storage = InMemoryStorage()
        task = storage.add(title="Buy groceries")
        assert isinstance(task, Task)
        assert task.id == 1
        assert task.title == "Buy groceries"

    def test_add_task_with_description(self) -> None:
        """Can add a task with both title and description."""
        storage = InMemoryStorage()
        task = storage.add(title="Shopping", description="Milk, eggs, bread")
        assert task.title == "Shopping"
        assert task.description == "Milk, eggs, bread"

    def test_add_task_increments_id(self) -> None:
        """Each new task gets an incremented ID."""
        storage = InMemoryStorage()
        task1 = storage.add(title="Task 1")
        task2 = storage.add(title="Task 2")
        task3 = storage.add(title="Task 3")
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_has_timestamps(self) -> None:
        """Added task has created_at and updated_at timestamps."""
        storage = InMemoryStorage()
        before = datetime.now()
        task = storage.add(title="Test task")
        after = datetime.now()
        assert before <= task.created_at <= after
        assert before <= task.updated_at <= after

    def test_add_task_defaults_to_not_completed(self) -> None:
        """Added task defaults to completed=False."""
        storage = InMemoryStorage()
        task = storage.add(title="New task")
        assert task.completed is False


class TestStorageGet:
    """Tests for InMemoryStorage.get() method."""

    def test_get_existing_task(self) -> None:
        """Can retrieve a task by ID."""
        storage = InMemoryStorage()
        added_task = storage.add(title="Test task")
        retrieved_task = storage.get(added_task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == added_task.id
        assert retrieved_task.title == added_task.title

    def test_get_nonexistent_task_returns_none(self) -> None:
        """Getting a non-existent task returns None."""
        storage = InMemoryStorage()
        result = storage.get(999)
        assert result is None

    def test_get_from_empty_storage_returns_none(self) -> None:
        """Getting from empty storage returns None."""
        storage = InMemoryStorage()
        result = storage.get(1)
        assert result is None


class TestStorageGetAll:
    """Tests for InMemoryStorage.get_all() method."""

    def test_get_all_returns_list(self) -> None:
        """get_all() returns a list."""
        storage = InMemoryStorage()
        result = storage.get_all()
        assert isinstance(result, list)

    def test_get_all_empty_storage(self) -> None:
        """get_all() returns empty list when storage is empty."""
        storage = InMemoryStorage()
        result = storage.get_all()
        assert result == []

    def test_get_all_returns_all_tasks(self) -> None:
        """get_all() returns all added tasks."""
        storage = InMemoryStorage()
        storage.add(title="Task 1")
        storage.add(title="Task 2")
        storage.add(title="Task 3")
        result = storage.get_all()
        assert len(result) == 3

    def test_get_all_ordered_by_creation(self) -> None:
        """get_all() returns tasks ordered by creation (newest first)."""
        storage = InMemoryStorage()
        storage.add(title="First")
        storage.add(title="Second")
        storage.add(title="Third")
        result = storage.get_all()
        # Newest first means Third (id=3) should be first
        assert result[0].title == "Third"
        assert result[1].title == "Second"
        assert result[2].title == "First"


class TestStorageUpdate:
    """Tests for InMemoryStorage.update() method."""

    def test_update_title(self) -> None:
        """Can update task title."""
        storage = InMemoryStorage()
        task = storage.add(title="Original")
        updated = storage.update(task.id, title="Updated")
        assert updated is not None
        assert updated.title == "Updated"

    def test_update_description(self) -> None:
        """Can update task description."""
        storage = InMemoryStorage()
        task = storage.add(title="Test", description="Original desc")
        updated = storage.update(task.id, description="New description")
        assert updated is not None
        assert updated.description == "New description"

    def test_update_both_title_and_description(self) -> None:
        """Can update both title and description."""
        storage = InMemoryStorage()
        task = storage.add(title="Original title", description="Original desc")
        updated = storage.update(task.id, title="New title", description="New desc")
        assert updated is not None
        assert updated.title == "New title"
        assert updated.description == "New desc"

    def test_update_nonexistent_task_returns_none(self) -> None:
        """Updating a non-existent task returns None."""
        storage = InMemoryStorage()
        result = storage.update(999, title="New title")
        assert result is None

    def test_update_preserves_unchanged_fields(self) -> None:
        """Updating one field preserves other fields."""
        storage = InMemoryStorage()
        task = storage.add(title="Original", description="Keep me")
        updated = storage.update(task.id, title="New title")
        assert updated is not None
        assert updated.description == "Keep me"
        assert updated.completed is False

    def test_update_changes_updated_at_timestamp(self) -> None:
        """Updating a task changes the updated_at timestamp."""
        storage = InMemoryStorage()
        task = storage.add(title="Test")
        original_updated_at = task.updated_at
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        updated = storage.update(task.id, title="New title")
        assert updated is not None
        assert updated.updated_at > original_updated_at


class TestStorageDelete:
    """Tests for InMemoryStorage.delete() method."""

    def test_delete_existing_task_returns_true(self) -> None:
        """Deleting an existing task returns True."""
        storage = InMemoryStorage()
        task = storage.add(title="To be deleted")
        result = storage.delete(task.id)
        assert result is True

    def test_delete_removes_task(self) -> None:
        """Deleted task is no longer retrievable."""
        storage = InMemoryStorage()
        task = storage.add(title="To be deleted")
        storage.delete(task.id)
        result = storage.get(task.id)
        assert result is None

    def test_delete_nonexistent_task_returns_false(self) -> None:
        """Deleting a non-existent task returns False."""
        storage = InMemoryStorage()
        result = storage.delete(999)
        assert result is False

    def test_delete_from_empty_storage_returns_false(self) -> None:
        """Deleting from empty storage returns False."""
        storage = InMemoryStorage()
        result = storage.delete(1)
        assert result is False

    def test_delete_does_not_affect_other_tasks(self) -> None:
        """Deleting one task does not affect others."""
        storage = InMemoryStorage()
        task1 = storage.add(title="Task 1")
        task2 = storage.add(title="Task 2")
        task3 = storage.add(title="Task 3")
        storage.delete(task2.id)
        assert storage.get(task1.id) is not None
        assert storage.get(task3.id) is not None
        assert len(storage.get_all()) == 2


class TestStorageMarkComplete:
    """Tests for InMemoryStorage.mark_complete() method."""

    def test_mark_complete_sets_completed_true(self) -> None:
        """mark_complete() sets completed to True."""
        storage = InMemoryStorage()
        task = storage.add(title="To complete")
        completed = storage.mark_complete(task.id)
        assert completed is not None
        assert completed.completed is True

    def test_mark_complete_nonexistent_returns_none(self) -> None:
        """mark_complete() on non-existent task returns None."""
        storage = InMemoryStorage()
        result = storage.mark_complete(999)
        assert result is None

    def test_mark_complete_updates_timestamp(self) -> None:
        """mark_complete() updates the updated_at timestamp."""
        storage = InMemoryStorage()
        task = storage.add(title="Test")
        original_updated_at = task.updated_at
        import time
        time.sleep(0.01)
        completed = storage.mark_complete(task.id)
        assert completed is not None
        assert completed.updated_at > original_updated_at

    def test_mark_complete_already_completed(self) -> None:
        """mark_complete() on already completed task keeps it completed."""
        storage = InMemoryStorage()
        task = storage.add(title="Test")
        storage.mark_complete(task.id)
        completed_again = storage.mark_complete(task.id)
        assert completed_again is not None
        assert completed_again.completed is True


class TestStorageHelperMethods:
    """Tests for helper methods like __len__ and __iter__."""

    def test_storage_len(self) -> None:
        """Can get number of tasks using len()."""
        storage = InMemoryStorage()
        assert len(storage) == 0
        storage.add(title="Task 1")
        assert len(storage) == 1
        storage.add(title="Task 2")
        assert len(storage) == 2

    def test_storage_is_initially_empty(self) -> None:
        """New storage is empty."""
        storage = InMemoryStorage()
        assert len(storage) == 0
        assert storage.get_all() == []
