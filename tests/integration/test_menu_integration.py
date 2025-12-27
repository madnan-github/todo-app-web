"""Integration tests for menu navigation flow (T011).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import patch, MagicMock

from rich.console import Console

from src.cli.menu import Menu
from src.storage.memory import InMemoryStorage


class TestMenuNavigation:
    """Tests for complete menu navigation flow."""

    def test_menu_exit_option_returns_exit_code(self) -> None:
        """Selecting Exit (6) returns appropriate signal."""
        menu = Menu()
        with patch.object(menu, '_prompt_input', return_value="6"):
            choice = menu.get_choice()
            assert choice == 6
            assert menu.is_exit_choice(choice)

    def test_menu_non_exit_options_not_exit(self) -> None:
        """Options 1-5 are not exit choices."""
        menu = Menu()
        for i in range(1, 6):
            assert menu.is_exit_choice(i) is False


class TestMenuWithStorage:
    """Tests for menu integration with storage."""

    def test_menu_can_be_created_without_storage(self) -> None:
        """Menu can be created standalone without storage."""
        menu = Menu()
        assert menu is not None

    def test_menu_accepts_console_injection(self) -> None:
        """Menu accepts console injection for testing."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)
        assert menu.console == console


class TestMenuLoop:
    """Tests for main menu loop behavior."""

    def test_menu_loop_continues_until_exit(self) -> None:
        """Menu loop continues until exit is selected."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)

        # Simulate: invalid input, option 1 (returns), option 6 (exit)
        call_count = [0]
        def mock_run_option(choice: int) -> bool:
            call_count[0] += 1
            if choice == 6:
                return False  # Exit
            return True  # Continue

        with patch.object(menu, '_prompt_input', side_effect=["1", "6"]):
            with patch.object(menu, 'run_option', side_effect=mock_run_option):
                menu.run_loop()

        # Should have run at least the exit
        assert call_count[0] >= 1


class TestGoodbyeMessage:
    """Tests for graceful exit with goodbye message (US6.4)."""

    def test_exit_shows_goodbye_message(self) -> None:
        """Exiting shows a goodbye/farewell message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)
        menu.show_goodbye()
        output_text = output.getvalue().lower()
        # Should contain some form of goodbye
        assert any(word in output_text for word in ["goodbye", "bye", "exit", "thank"])


class TestMenuPrompt:
    """Tests for menu prompt display."""

    def test_menu_shows_prompt_text(self) -> None:
        """Menu displays prompt asking for choice."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)
        menu.display()
        output_text = output.getvalue().lower()
        # Should contain prompt-related text
        assert any(word in output_text for word in ["choice", "select", "option", "enter"])
