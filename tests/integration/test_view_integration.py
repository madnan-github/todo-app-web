"""Integration tests for view tasks flow (T024).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO

from rich.console import Console

from src.commands.view import ViewTasksCommand
from src.commands.add import AddTaskCommand
from src.storage.memory import InMemoryStorage


class TestViewTasksIntegration:
    """Integration tests for complete view tasks flow."""

    def test_view_after_add(self) -> None:
        """Can view tasks after adding them."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()

        # Add a task directly
        storage.add(title="Added task", description="Description")

        # View tasks
        view_command = ViewTasksCommand(storage, console)
        view_command.execute()

        output_text = output.getvalue()
        assert "Added task" in output_text

    def test_view_shows_completed_and_pending(self) -> None:
        """View shows both completed and pending tasks."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()

        # Add tasks
        pending_task = storage.add(title="Pending task")
        completed_task = storage.add(title="Completed task")
        storage.mark_complete(completed_task.id)

        # View
        view_command = ViewTasksCommand(storage, console)
        view_command.execute()

        output_text = output.getvalue()
        assert "Pending task" in output_text
        assert "Completed task" in output_text


class TestViewTasksWithLargeList:
    """Tests for viewing larger task lists."""

    def test_view_many_tasks(self) -> None:
        """Can view many tasks without error."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()

        # Add 20 tasks
        for i in range(20):
            storage.add(title=f"Task number {i + 1}")

        view_command = ViewTasksCommand(storage, console)
        view_command.execute()

        output_text = output.getvalue()
        assert "Task number 1" in output_text
        assert "Task number 20" in output_text


class TestViewTasksOutput:
    """Tests for view output formatting."""

    def test_output_is_styled(self) -> None:
        """Output uses Rich styling."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue()
        # Rich output should exist
        assert len(output_text) > 0

    def test_empty_list_message_is_friendly(self) -> None:
        """Empty list shows user-friendly message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue().lower()
        # Should be informative, not just empty
        assert len(output_text) > 10
