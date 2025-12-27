"""Unit tests for UpdateTaskCommand (T038).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

from src.commands.update import UpdateTaskCommand
from src.storage.memory import InMemoryStorage


class TestUpdateTaskExecution:
    """Tests for UpdateTaskCommand execute method."""

    def test_update_title_changes_task(self) -> None:
        """Updating title changes the task title."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Original title", description="Original desc")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value="New title"):
                with patch.object(command, '_prompt_new_description', return_value=""):
                    command.execute()

        task = storage.get(1)
        assert task.title == "New title"

    def test_update_description_changes_task(self) -> None:
        """Updating description changes the task description."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Title", description="Original desc")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value=""):
                with patch.object(command, '_prompt_new_description', return_value="New description"):
                    command.execute()

        task = storage.get(1)
        assert task.description == "New description"

    def test_update_shows_success_message(self) -> None:
        """Updating task shows success message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value="Updated"):
                with patch.object(command, '_prompt_new_description', return_value=""):
                    command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["success", "updated", "changed"])


class TestUpdateTaskValidation:
    """Tests for update input validation."""

    def test_invalid_id_shows_error(self) -> None:
        """Invalid task ID shows error message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', side_effect=["abc", "1"]):
            with patch.object(command, '_prompt_new_title', return_value="Updated"):
                with patch.object(command, '_prompt_new_description', return_value=""):
                    command.execute()

        output_text = output.getvalue().lower()
        assert "error" in output_text or "invalid" in output_text

    def test_nonexistent_task_shows_error(self) -> None:
        """Non-existent task ID shows not found error."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Test task")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', side_effect=["999", "1"]):
            with patch.object(command, '_prompt_new_title', return_value="Updated"):
                with patch.object(command, '_prompt_new_description', return_value=""):
                    command.execute()

        output_text = output.getvalue().lower()
        assert any(word in output_text for word in ["not found", "doesn't exist"])

    def test_empty_title_on_update_shows_error(self) -> None:
        """Empty title on update (when trying to clear) shows error."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Original", description="Desc")

        command = UpdateTaskCommand(storage, console)
        # Skip with empty means keep original
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value=""):
                with patch.object(command, '_prompt_new_description', return_value=""):
                    command.execute()

        # Should keep original when both are empty (skip)
        task = storage.get(1)
        assert task.title == "Original"


class TestUpdateTaskSkipFields:
    """Tests for skipping fields during update."""

    def test_skip_title_keeps_original(self) -> None:
        """Pressing Enter (empty) for title keeps original."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Original title", description="Original desc")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value=""):  # Skip
                with patch.object(command, '_prompt_new_description', return_value="New desc"):
                    command.execute()

        task = storage.get(1)
        assert task.title == "Original title"
        assert task.description == "New desc"

    def test_skip_description_keeps_original(self) -> None:
        """Pressing Enter (empty) for description keeps original."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="Original title", description="Original desc")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value="New title"):
                with patch.object(command, '_prompt_new_description', return_value=""):  # Skip
                    command.execute()

        task = storage.get(1)
        assert task.title == "New title"
        assert task.description == "Original desc"


class TestUpdateTaskShowsCurrent:
    """Tests for showing current values."""

    def test_shows_current_title(self) -> None:
        """Update prompts show current title value."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        storage.add(title="My Current Title")

        command = UpdateTaskCommand(storage, console)
        with patch.object(command, '_prompt_task_id', return_value="1"):
            with patch.object(command, '_prompt_new_title', return_value="New"):
                with patch.object(command, '_prompt_new_description', return_value=""):
                    command.execute()

        output_text = output.getvalue()
        assert "My Current Title" in output_text


class TestUpdateTaskCommandStructure:
    """Tests for command structure compliance."""

    def test_update_command_is_command_subclass(self) -> None:
        """UpdateTaskCommand is a proper Command subclass."""
        from src.commands.base import Command
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()
        command = UpdateTaskCommand(storage, console)
        assert isinstance(command, Command)
