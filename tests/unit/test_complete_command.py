"""Unit tests for MarkCompleteCommand (T030).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

from src.commands.complete import MarkCompleteCommand
from src.storage.memory import InMemoryStorage


class TestMarkCompleteExecution:
    """Tests for MarkCompleteCommand execute method."""

    def test_mark_complete_changes_status(self) -> None:
        """Marking complete changes task status to True."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        task = storage.add(title="Test task")
        assert task.completed is False

        command = MarkCompleteCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        updated_task = storage.get(1)
        assert updated_task is not None
        assert updated_task.completed is True

    def test_mark_complete_shows_success_message(self) -> None:
        """Marking complete shows success message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")

        command = MarkCompleteCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["success", "complete", "done", "marked"])


class TestMarkCompleteValidation:
    """Tests for input validation."""

    def test_invalid_id_shows_error(self) -> None:
        """Invalid task ID shows error message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")

        command = MarkCompleteCommand(storage, console)
        # First invalid, then valid
        with patch.object(command, '_prompt_task_id', side_effect=["abc", "1"]):
            command.execute()

        output_text = output.getvalue().lower()
        assert "error" in output_text or "invalid" in output_text

    def test_nonexistent_task_shows_error(self) -> None:
        """Non-existent task ID shows not found error."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")  # ID 1

        command = MarkCompleteCommand(storage, console)
        with patch.object(command, '_prompt_task_id', side_effect=["999", "1"]):
            command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["not found", "doesn't exist", "does not exist"])


class TestMarkCompleteAlreadyCompleted:
    """Tests for marking already completed task."""

    def test_already_completed_shows_info_message(self) -> None:
        """Marking already completed task shows info message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        task = storage.add(title="Test task")
        storage.mark_complete(task.id)

        command = MarkCompleteCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["already", "completed", "done"])


class TestMarkCompletePrompt:
    """Tests for ID prompt."""

    def test_prompts_for_task_id(self) -> None:
        """MarkCompleteCommand prompts for task ID."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test")

        command = MarkCompleteCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1") as mock_prompt:
            command.execute()

        mock_prompt.assert_called()


class TestMarkCompleteCommandStructure:
    """Tests for command structure compliance."""

    def test_complete_command_is_command_subclass(self) -> None:
        """MarkCompleteCommand is a proper Command subclass."""
        from src.commands.base import Command
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = MarkCompleteCommand(storage, console)
        assert isinstance(command, Command)

    def test_complete_command_has_execute_method(self) -> None:
        """MarkCompleteCommand has execute method."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = MarkCompleteCommand(storage, console)
        assert hasattr(command, 'execute')
        assert callable(command.execute)
