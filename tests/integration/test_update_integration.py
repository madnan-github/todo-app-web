"""Integration tests for update task flow (T039).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

from src.commands.update import UpdateTaskCommand
from src.storage.memory import InMemoryStorage


class TestUpdateTaskIntegration:
    """Integration tests for complete update task flow."""

    def test_update_both_fields(self) -> None:
        """Can update both title and description."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Original", description="Original desc")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value="New title"):
                with patch.object(command, '_prompt_new_description', return_value="New desc"):
                    command.execute()

        task = storage.get(1)
        assert task.title == "New title"
        assert task.description == "New desc"

    def test_update_preserves_completed_status(self) -> None:
        """Update preserves task completed status."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        task = storage.add(title="Original")
        storage.mark_complete(task.id)

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value="Updated"):
                with patch.object(command, '_prompt_new_description', return_value=""):
                    command.execute()

        updated_task = storage.get(1)
        assert updated_task.completed is True


class TestUpdateTaskEdgeCases:
    """Edge case tests for update task."""

    def test_update_empty_storage(self) -> None:
        """Handling update on empty storage."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()

        command = UpdateTaskCommand(storage, console)
        command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["no task", "empty", "add"])

    def test_update_multiple_tasks_independently(self) -> None:
        """Can update different tasks independently."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Task 1")
        storage.add(title="Task 2")
        storage.add(title="Task 3")

        command = UpdateTaskCommand(storage, console)

        # Update task 2
        with patch.object(command, '_prompt_task_id', return_value="2"):
            with patch.object(command, '_prompt_new_title', return_value="Updated Task 2"):
                with patch.object(command, '_prompt_new_description', return_value=""):
                    command.execute()

        assert storage.get(1).title == "Task 1"  # Unchanged
        assert storage.get(2).title == "Updated Task 2"  # Changed
        assert storage.get(3).title == "Task 3"  # Unchanged
