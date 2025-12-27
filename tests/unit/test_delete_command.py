"""Unit tests for DeleteTaskCommand (T047).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

from src.commands.delete import DeleteTaskCommand
from src.storage.memory import InMemoryStorage


class TestDeleteTaskExecution:
    """Tests for DeleteTaskCommand execute method."""

    def test_delete_removes_task_from_storage(self) -> None:
        """Deleting task removes it from storage."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Task to delete")
        assert len(storage) == 1

        command = DeleteTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        assert len(storage) == 0
        assert storage.get(1) is None

    def test_delete_shows_success_message(self) -> None:
        """Deleting task shows success message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")

        command = DeleteTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["success", "deleted", "removed"])


class TestDeleteTaskValidation:
    """Tests for input validation."""

    def test_invalid_id_shows_error(self) -> None:
        """Invalid task ID shows error message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")

        command = DeleteTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', side_effect=["abc", "1"]):
            command.execute()

        output_text = output.getvalue().lower()
        assert "error" in output_text or "invalid" in output_text

    def test_nonexistent_task_shows_error(self) -> None:
        """Non-existent task ID shows not found error."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")

        command = DeleteTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', side_effect=["999", "1"]):
            command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["not found", "doesn't exist"])


class TestDeleteTaskPrompt:
    """Tests for ID prompt."""

    def test_prompts_for_task_id(self) -> None:
        """DeleteTaskCommand prompts for task ID."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test")

        command = DeleteTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1") as mock_prompt:
            command.execute()

        mock_prompt.assert_called()


class TestDeleteTaskDoesNotAffectOthers:
    """Tests for isolation of delete operation."""

    def test_delete_does_not_affect_other_tasks(self) -> None:
        """Deleting one task does not affect others."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Task 1")
        storage.add(title="Task 2")
        storage.add(title="Task 3")

        command = DeleteTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="2"):
            command.execute()

        assert storage.get(1) is not None
        assert storage.get(2) is None  # Deleted
        assert storage.get(3) is not None
        assert len(storage) == 2


class TestDeleteTaskCommandStructure:
    """Tests for command structure compliance."""

    def test_delete_command_is_command_subclass(self) -> None:
        """DeleteTaskCommand is a proper Command subclass."""
        from src.commands.base import Command
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = DeleteTaskCommand(storage, console)
        assert isinstance(command, Command)

    def test_delete_command_has_execute_method(self) -> None:
        """DeleteTaskCommand has execute method."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = DeleteTaskCommand(storage, console)
        assert hasattr(command, 'execute')
        assert callable(command.execute)
