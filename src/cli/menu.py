"""Rich-based menu system (T012-T015).

This module provides the main menu interface for the Todo application.
Uses Rich library for beautiful terminal output.
"""

from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text


@dataclass
class MenuOption:
    """Represents a menu option.

    Attributes:
        number: The option number (1-6)
        label: The display label for the option
    """

    number: int
    label: str


class Menu:
    """Main menu interface for the Todo application.

    Provides menu display, input handling, and navigation.
    Uses Rich library for styled terminal output.

    Attributes:
        console: Rich Console for output
        options: List of menu options
    """

    EXIT_OPTION = 6

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the menu.

        Args:
            console: Optional Rich Console (for testing)
        """
        self.console = console or Console()
        self.options = [
            MenuOption(1, "Add Task"),
            MenuOption(2, "View Tasks"),
            MenuOption(3, "Update Task"),
            MenuOption(4, "Delete Task"),
            MenuOption(5, "Mark Complete"),
            MenuOption(6, "Exit"),
        ]
        self._option_handler: dict[int, callable] = {}

    def display(self) -> None:
        """Display the menu with all options."""
        # Display title
        title = Text("Todo App", style="bold cyan")
        self.console.print(Panel(title, expand=False))
        self.console.print()

        # Display menu options in a table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Number", style="cyan", justify="right")
        table.add_column("Option", style="white")

        for option in self.options:
            style = "dim" if option.number == self.EXIT_OPTION else ""
            table.add_row(f"[{option.number}]", option.label, style=style)

        self.console.print(table)
        self.console.print()
        self.console.print("Enter your choice (1-6):", style="bold")

    def validate_input(self, user_input: str) -> bool:
        """Validate menu input.

        Args:
            user_input: The user's input string

        Returns:
            True if valid (1-6), False otherwise
        """
        try:
            value = int(user_input.strip())
            return 1 <= value <= 6
        except (ValueError, AttributeError):
            return False

    def _prompt_input(self) -> str:
        """Get raw input from user.

        This is separated for easier testing/mocking.

        Returns:
            User's input string
        """
        return Prompt.ask("", console=self.console)

    def get_choice(self) -> int:
        """Get a valid menu choice from user.

        Continues prompting until valid input received.

        Returns:
            Valid menu option number (1-6)
        """
        while True:
            user_input = self._prompt_input()
            if self.validate_input(user_input):
                return int(user_input.strip())
            self.show_error("Invalid choice. Please enter a number from 1 to 6.")

    def show_error(self, message: str) -> None:
        """Display an error message.

        Args:
            message: The error message to display
        """
        self.console.print(f"[bold red]Error:[/bold red] {message}")

    def show_success(self, message: str) -> None:
        """Display a success message.

        Args:
            message: The success message to display
        """
        self.console.print(f"[bold green]Success:[/bold green] {message}")

    def show_info(self, message: str) -> None:
        """Display an info message.

        Args:
            message: The info message to display
        """
        self.console.print(f"[bold blue]Info:[/bold blue] {message}")

    def is_exit_choice(self, choice: int) -> bool:
        """Check if choice is the exit option.

        Args:
            choice: Menu choice number

        Returns:
            True if exit choice, False otherwise
        """
        return choice == self.EXIT_OPTION

    def show_goodbye(self) -> None:
        """Display goodbye message on exit."""
        self.console.print()
        self.console.print(
            Panel(
                "[bold cyan]Goodbye![/bold cyan] Thank you for using Todo App.",
                expand=False,
            )
        )

    def register_handler(self, option: int, handler: callable) -> None:
        """Register a handler for a menu option.

        Args:
            option: Menu option number
            handler: Function to call when option selected
        """
        self._option_handler[option] = handler

    def run_option(self, choice: int) -> bool:
        """Run the handler for a menu option.

        Args:
            choice: The menu option number

        Returns:
            False if exit, True to continue
        """
        if self.is_exit_choice(choice):
            return False

        handler = self._option_handler.get(choice)
        if handler:
            handler()
        else:
            self.show_info(f"Option {choice} not yet implemented")

        return True

    def run_loop(self) -> None:
        """Run the main menu loop.

        Displays menu, gets choice, executes handler.
        Continues until exit is selected.
        """
        while True:
            self.display()
            choice = self.get_choice()
            if not self.run_option(choice):
                self.show_goodbye()
                break
            self.console.print()  # Spacing between operations
