"""Unit tests for AddTaskCommand (T016).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch, MagicMock

from rich.console import Console

from src.commands.add import AddTaskCommand
from src.storage.memory import InMemoryStorage


class TestAddTaskCommandExecution:
    """Tests for AddTaskCommand execute method."""

    def test_add_task_creates_task_in_storage(self) -> None:
        """Adding a task stores it in storage."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', return_value="Buy groceries"):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        assert len(storage) == 1
        tasks = storage.get_all()
        assert tasks[0].title == "Buy groceries"

    def test_add_task_with_description(self) -> None:
        """Can add task with both title and description."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', return_value="Shopping"):
            with patch.object(command, '_prompt_description', return_value="Milk, eggs"):
                command.execute()

        task = storage.get(1)
        assert task is not None
        assert task.title == "Shopping"
        assert task.description == "Milk, eggs"

    def test_add_task_shows_success_message(self) -> None:
        """Adding a task shows success confirmation."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', return_value="Test task"):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        output_text = output.getvalue().lower()
        # Should contain success-related text
        assert any(word in output_text for word in ["success", "added", "created"])


class TestAddTaskValidation:
    """Tests for input validation during add task."""

    def test_empty_title_shows_error(self) -> None:
        """Empty title displays error and reprompts."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        # First empty, then valid
        with patch.object(command, '_prompt_title', side_effect=["", "Valid title"]):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        output_text = output.getvalue().lower()
        assert "error" in output_text or "empty" in output_text
        # Task should still be created with valid title
        assert len(storage) == 1

    def test_whitespace_only_title_shows_error(self) -> None:
        """Whitespace-only title displays error."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', side_effect=["   ", "Valid title"]):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        output_text = output.getvalue().lower()
        assert "error" in output_text or "empty" in output_text

    def test_title_too_long_shows_error(self) -> None:
        """Title over 200 chars displays error."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        long_title = "a" * 201
        with patch.object(command, '_prompt_title', side_effect=[long_title, "Valid title"]):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        output_text = output.getvalue().lower()
        assert "error" in output_text or "200" in output_text

    def test_description_too_long_shows_error(self) -> None:
        """Description over 1000 chars displays error."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        long_desc = "a" * 1001
        with patch.object(command, '_prompt_title', return_value="Test"):
            with patch.object(command, '_prompt_description', side_effect=[long_desc, "Valid desc"]):
                command.execute()

        output_text = output.getvalue().lower()
        assert "error" in output_text or "1000" in output_text


class TestAddTaskPrompts:
    """Tests for input prompts."""

    def test_prompts_for_title(self) -> None:
        """AddTaskCommand prompts for title."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', return_value="Test") as mock_title:
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        mock_title.assert_called()

    def test_prompts_for_description(self) -> None:
        """AddTaskCommand prompts for description."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', return_value="Test"):
            with patch.object(command, '_prompt_description', return_value="") as mock_desc:
                command.execute()

        mock_desc.assert_called()


class TestAddTaskCancellation:
    """Tests for cancelling add task operation."""

    def test_cancel_with_empty_title_multiple_times(self) -> None:
        """User can keep getting errors until valid input."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = AddTaskCommand(storage, console)

        with patch.object(command, '_prompt_title', side_effect=["", "", "Finally valid"]):
            with patch.object(command, '_prompt_description', return_value=""):
                command.execute()

        assert len(storage) == 1
