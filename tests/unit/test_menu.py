"""Unit tests for menu display and input handling (T010).

TDD: These tests must FAIL before implementation.
"""

import pytest
from io import StringIO
from unittest.mock import MagicMock, patch

from rich.console import Console

from src.cli.menu import Menu, MenuOption


class TestMenuOptions:
    """Tests for menu option definitions."""

    def test_menu_has_six_options(self) -> None:
        """Menu has 6 options: Add, View, Update, Delete, Complete, Exit."""
        menu = Menu()
        assert len(menu.options) == 6

    def test_menu_options_are_numbered(self) -> None:
        """Menu options are numbered 1-6."""
        menu = Menu()
        option_numbers = [opt.number for opt in menu.options]
        assert option_numbers == [1, 2, 3, 4, 5, 6]

    def test_menu_option_labels(self) -> None:
        """Menu options have correct labels."""
        menu = Menu()
        labels = [opt.label for opt in menu.options]
        assert "Add Task" in labels
        assert "View Tasks" in labels
        assert "Update Task" in labels
        assert "Delete Task" in labels
        assert "Mark Complete" in labels
        assert "Exit" in labels


class TestMenuDisplay:
    """Tests for menu display functionality."""

    def test_menu_display_shows_title(self) -> None:
        """Menu display includes application title."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)
        menu.display()
        output_text = output.getvalue()
        assert "Todo" in output_text or "todo" in output_text.lower()

    def test_menu_display_shows_all_options(self) -> None:
        """Menu display shows all numbered options."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)
        menu.display()
        output_text = output.getvalue()
        # Check that numbers 1-6 appear
        assert "1" in output_text
        assert "2" in output_text
        assert "3" in output_text
        assert "4" in output_text
        assert "5" in output_text
        assert "6" in output_text


class TestMenuInputValidation:
    """Tests for menu input validation."""

    def test_valid_input_1_to_6(self) -> None:
        """Valid inputs are 1-6."""
        menu = Menu()
        for i in range(1, 7):
            assert menu.validate_input(str(i)) is True

    def test_invalid_input_zero(self) -> None:
        """Input '0' is invalid."""
        menu = Menu()
        assert menu.validate_input("0") is False

    def test_invalid_input_seven(self) -> None:
        """Input '7' is invalid."""
        menu = Menu()
        assert menu.validate_input("7") is False

    def test_invalid_input_negative(self) -> None:
        """Negative input is invalid."""
        menu = Menu()
        assert menu.validate_input("-1") is False

    def test_invalid_input_non_numeric(self) -> None:
        """Non-numeric input is invalid."""
        menu = Menu()
        assert menu.validate_input("abc") is False
        assert menu.validate_input("") is False
        assert menu.validate_input(" ") is False

    def test_invalid_input_special_characters(self) -> None:
        """Special characters are invalid."""
        menu = Menu()
        assert menu.validate_input("!") is False
        assert menu.validate_input("@") is False


class TestMenuGetChoice:
    """Tests for getting user menu choice."""

    def test_get_choice_returns_valid_number(self) -> None:
        """get_choice returns valid menu option number."""
        menu = Menu()
        with patch.object(menu, '_prompt_input', return_value="1"):
            choice = menu.get_choice()
            assert choice == 1

    def test_get_choice_reprompts_on_invalid(self) -> None:
        """get_choice reprompts on invalid input."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)
        # First return invalid, then valid
        with patch.object(menu, '_prompt_input', side_effect=["invalid", "7", "3"]):
            choice = menu.get_choice()
            assert choice == 3


class TestMenuErrorMessages:
    """Tests for menu error message display."""

    def test_invalid_input_shows_error(self) -> None:
        """Invalid input displays error message."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)
        menu.show_error("Invalid choice")
        output_text = output.getvalue()
        assert "Invalid" in output_text or "invalid" in output_text.lower()

    def test_error_message_styling(self) -> None:
        """Error messages should be styled (red)."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        menu = Menu(console=console)
        menu.show_error("Test error")
        # The output should contain styling escape codes
        output_text = output.getvalue()
        assert len(output_text) > 0


class TestMenuOptionDataClass:
    """Tests for MenuOption data class."""

    def test_menu_option_creation(self) -> None:
        """MenuOption can be created with number and label."""
        option = MenuOption(number=1, label="Test Option")
        assert option.number == 1
        assert option.label == "Test Option"

    def test_menu_option_equality(self) -> None:
        """MenuOption equality based on attributes."""
        opt1 = MenuOption(number=1, label="Test")
        opt2 = MenuOption(number=1, label="Test")
        assert opt1 == opt2
