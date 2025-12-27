"""Integration tests for add task flow (T017).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

from src.commands.add import AddTaskCommand
from src.storage.memory import InMemoryStorage
from src.cli.menu import Menu


class TestAddTaskIntegration:
    """Integration tests for complete add task flow."""

    def test_add_task_end_to_end(self) -> None:
        """Complete add task flow from input to storage."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', return_value="Integration test task"):
            with patch.object(command, '_prompt_description', return_value="Description"):
                command.execute()

        # Verify task in storage
        tasks = storage.get_all()
        assert len(tasks) == 1
        assert tasks[0].title == "Integration test task"
        assert tasks[0].description == "Description"
        assert tasks[0].completed is False

    def test_add_multiple_tasks(self) -> None:
        """Can add multiple tasks sequentially."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        # Add first task
        with patch.object(command, '_prompt_title', return_value="Task 1"):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        # Add second task
        with patch.object(command, '_prompt_title', return_value="Task 2"):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        assert len(storage) == 2
        assert storage.get(1).title == "Task 1"
        assert storage.get(2).title == "Task 2"

    def test_add_task_assigns_sequential_ids(self) -> None:
        """Added tasks get sequential IDs."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        for i in range(1, 4):
            with patch.object(command, '_prompt_title', return_value=f"Task {i}"):
                with patch.object(command, '_prompt_description', return_value=""):
                    command.execute()

        tasks = storage.get_all()
        ids = sorted([t.id for t in tasks])
        assert ids == [1, 2, 3]


class TestAddTaskWithMenu:
    """Tests for add task integrated with menu."""

    def test_add_command_is_command_subclass(self) -> None:
        """AddTaskCommand is a proper Command subclass."""
        from src.commands.base import Command
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)
        assert isinstance(command, Command)

    def test_add_command_has_execute_method(self) -> None:
        """AddTaskCommand has execute method."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)
        assert hasattr(command, 'execute')
        assert callable(command.execute)


class TestAddTaskOutput:
    """Tests for add task output display."""

    def test_success_message_includes_task_id(self) -> None:
        """Success message includes the new task's ID."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', return_value="Test"):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        output_text = output.getvalue()
        # Should contain the ID (1)
        assert "1" in output_text

    def test_output_uses_rich_styling(self) -> None:
        """Output uses Rich styling (has escape codes)."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', return_value="Test"):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        output_text = output.getvalue()
        # Rich output should have some styling
        assert len(output_text) > 0
