"""Integration tests for delete task flow (T048).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

from src.commands.delete import DeleteTaskCommand
from src.commands.view import ViewTasksCommand
from src.storage.memory import InMemoryStorage


class TestDeleteTaskIntegration:
    """Integration tests for complete delete task flow."""

    def test_deleted_task_not_in_view(self) -> None:
        """Deleted task does not appear in view."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Task to delete")
        storage.add(title="Task to keep")

        # Delete first task
        delete_command = DeleteTaskCommand(storage, console)
        with patch.object(delete_command, '_prompt_task_id', return_value="1"):
            delete_command.execute()

        # Clear output and view
        output.truncate(0)
        output.seek(0)
        view_command = ViewTasksCommand(storage, console)
        view_command.execute()

        output_text = output.getvalue()
        assert "Task to delete" not in output_text
        assert "Task to keep" in output_text

    def test_delete_multiple_tasks(self) -> None:
        """Can delete multiple tasks."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Task 1")
        storage.add(title="Task 2")
        storage.add(title="Task 3")

        command = DeleteTaskCommand(storage, console)

        # Delete task 1
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        # Delete task 3
        with patch.object(command, '_prompt_task_id', return_value="3"):
            command.execute()

        assert storage.get(1) is None
        assert storage.get(2) is not None
        assert storage.get(3) is None
        assert len(storage) == 1


class TestDeleteTaskEdgeCases:
    """Edge case tests for delete task."""

    def test_delete_empty_storage(self) -> None:
        """Handling delete on empty storage."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()

        command = DeleteTaskCommand(storage, console)
        command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["no task", "empty", "add"])

    def test_delete_last_task(self) -> None:
        """Can delete the last remaining task."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Only task")

        command = DeleteTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        assert len(storage) == 0

    def test_delete_completed_task(self) -> None:
        """Can delete a completed task."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        task = storage.add(title="Completed task")
        storage.mark_complete(task.id)

        command = DeleteTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        assert storage.get(1) is None
