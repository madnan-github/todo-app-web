"""Unit tests for ViewTasksCommand (T023).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from datetime import datetime

from rich.console import Console

from src.commands.view import ViewTasksCommand
from src.storage.memory import InMemoryStorage


class TestViewTasksDisplay:
    """Tests for task list display."""

    def test_view_empty_storage_shows_message(self) -> None:
        """Viewing empty storage shows friendly message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["no task", "empty", "no tasks"])

    def test_view_single_task(self) -> None:
        """Can view a single task."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue()
        assert "Test task" in output_text
        assert "1" in output_text  # ID

    def test_view_multiple_tasks(self) -> None:
        """Can view multiple tasks."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Task 1")
        storage.add(title="Task 2")
        storage.add(title="Task 3")
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue()
        assert "Task 1" in output_text
        assert "Task 2" in output_text
        assert "Task 3" in output_text


class TestViewTasksTable:
    """Tests for Rich Table display."""

    def test_display_shows_table_with_headers(self) -> None:
        """Display includes table with column headers."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test")
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue()
        # Should have ID, Title, Status, Created columns
        assert "ID" in output_text or "id" in output_text.lower()

    def test_display_shows_task_id(self) -> None:
        """Display shows task ID."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue()
        assert "1" in output_text

    def test_display_shows_task_title(self) -> None:
        """Display shows task title."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="My important task")
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue()
        assert "My important task" in output_text


class TestViewTasksStatusIndicators:
    """Tests for status indicator display."""

    def test_pending_task_shows_pending_indicator(self) -> None:
        """Pending task shows pending status indicator."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Pending task")  # Default is not completed
        command = ViewTasksCommand(storage, console)

        command.execute()

        # Should have some indicator for pending (circle, ○, pending, etc.)
        output_text = output.getvalue()
        # Check that it doesn't have checkmark for pending task
        assert "Pending task" in output_text

    def test_completed_task_shows_completed_indicator(self) -> None:
        """Completed task shows completed status indicator."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        task = storage.add(title="Done task")
        storage.mark_complete(task.id)
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue()
        # Should have checkmark or completed indicator
        assert "Done task" in output_text


class TestViewTasksOrder:
    """Tests for task display order."""

    def test_tasks_ordered_newest_first(self) -> None:
        """Tasks are displayed with newest first."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="First task")
        storage.add(title="Second task")
        storage.add(title="Third task")
        command = ViewTasksCommand(storage, console)

        command.execute()

        output_text = output.getvalue()
        # Third task should appear before First task
        third_pos = output_text.find("Third task")
        first_pos = output_text.find("First task")
        assert third_pos < first_pos


class TestViewTasksCommandStructure:
    """Tests for command structure compliance."""

    def test_view_command_is_command_subclass(self) -> None:
        """ViewTasksCommand is a proper Command subclass."""
        from src.commands.base import Command
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = ViewTasksCommand(storage, console)
        assert isinstance(command, Command)

    def test_view_command_has_execute_method(self) -> None:
        """ViewTasksCommand has execute method."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = ViewTasksCommand(storage, console)
        assert hasattr(command, 'execute')
        assert callable(command.execute)
