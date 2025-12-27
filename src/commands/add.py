"""AddTaskCommand implementation (T018-T022).

This module implements the Add Task command for creating new tasks.
"""

from pydantic import ValidationError
from rich.console import Console
from rich.prompt import Prompt

from src.commands.base import Command
from src.storage.memory import InMemoryStorage


class AddTaskCommand(Command):
    """Command for adding a new task.

    Prompts user for title and optional description,
    validates input, and creates a new task in storage.
    """

    TITLE_MAX_LENGTH = 200
    DESCRIPTION_MAX_LENGTH = 1000

    def __init__(self, storage: InMemoryStorage, console: Console) -> None:
        """Initialize AddTaskCommand.

        Args:
            storage: InMemoryStorage instance
            console: Rich Console instance
        """
        super().__init__(storage, console)

    def execute(self) -> None:
        """Execute the add task command.

        Prompts for title and description, validates input,
        and creates a new task in storage.
        """
        self.console.print("\n[bold cyan]Add New Task[/bold cyan]")
        self.console.print("-" * 30)

        # Get valid title
        title = self._get_valid_title()

        # Get valid description
        description = self._get_valid_description()

        # Create the task
        task = self.storage.add(title=title, description=description)

        # Show success message
        self.console.print()
        self.console.print(
            f"[bold green]Success![/bold green] Task #{task.id} added: {task.title}"
        )

    def _get_valid_title(self) -> str:
        """Get a valid title from user.

        Continues prompting until valid title is entered.

        Returns:
            Valid task title
        """
        while True:
            title = self._prompt_title()

            # Check empty/whitespace
            if not title or not title.strip():
                self.console.print(
                    "[bold red]Error:[/bold red] Title cannot be empty."
                )
                continue

            # Check length
            if len(title.strip()) > self.TITLE_MAX_LENGTH:
                self.console.print(
                    f"[bold red]Error:[/bold red] Title must be {self.TITLE_MAX_LENGTH} characters or less."
                )
                continue

            return title.strip()

    def _get_valid_description(self) -> str:
        """Get a valid description from user.

        Continues prompting until valid description is entered.

        Returns:
            Valid task description (may be empty)
        """
        while True:
            description = self._prompt_description()

            # Empty is okay
            if not description:
                return ""

            # Check length
            if len(description.strip()) > self.DESCRIPTION_MAX_LENGTH:
                self.console.print(
                    f"[bold red]Error:[/bold red] Description must be {self.DESCRIPTION_MAX_LENGTH} characters or less."
                )
                continue

            return description.strip()

    def _prompt_title(self) -> str:
        """Prompt user for task title.

        Returns:
            User's input for title
        """
        return Prompt.ask(
            "[bold]Title[/bold]",
            console=self.console,
        )

    def _prompt_description(self) -> str:
        """Prompt user for task description.

        Returns:
            User's input for description (may be empty)
        """
        return Prompt.ask(
            "[bold]Description[/bold] (optional)",
            console=self.console,
            default="",
        )
