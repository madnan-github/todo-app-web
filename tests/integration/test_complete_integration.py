"""Integration tests for mark complete flow (T031).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

from src.commands.complete import MarkCompleteCommand
from src.commands.view import ViewTasksCommand
from src.storage.memory import InMemoryStorage


class TestMarkCompleteIntegration:
    """Integration tests for complete mark complete flow."""

    def test_mark_complete_shows_in_view(self) -> None:
        """Marked complete task shows as completed in view."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Task to complete")

        # Mark complete
        complete_command = MarkCompleteCommand(storage, console)
        with patch.object(complete_command, '_prompt_task_id', return_value="1"):
            complete_command.execute()

        # Clear output and view
        output.truncate(0)
        output.seek(0)
        view_command = ViewTasksCommand(storage, console)
        view_command.execute()

        # Task should show as completed
        task = storage.get(1)
        assert task.completed is True

    def test_complete_multiple_tasks(self) -> None:
        """Can complete multiple tasks."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Task 1")
        storage.add(title="Task 2")
        storage.add(title="Task 3")

        command = MarkCompleteCommand(storage, console)

        # Complete task 1
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        # Complete task 3
        with patch.object(command, '_prompt_task_id', return_value="3"):
            command.execute()

        assert storage.get(1).completed is True
        assert storage.get(2).completed is False
        assert storage.get(3).completed is True


class TestMarkCompleteEdgeCases:
    """Edge case tests for mark complete."""

    def test_complete_empty_storage(self) -> None:
        """Handling mark complete on empty storage."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()

        command = MarkCompleteCommand(storage, console)
        # Should handle gracefully - show no tasks message
        command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["no task", "empty", "add"])

    def test_complete_preserves_other_task_data(self) -> None:
        """Completing a task preserves its title and description."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="My task", description="My description")

        command = MarkCompleteCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        task = storage.get(1)
        assert task.title == "My task"
        assert task.description == "My description"
        assert task.completed is True
