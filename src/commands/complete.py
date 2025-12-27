"""MarkCompleteCommand implementation (T032-T037).

This module implements the Mark Complete command for completing tasks.
"""

from rich.console import Console
from rich.prompt import Prompt

from src.commands.base import Command
from src.storage.memory import InMemoryStorage


class MarkCompleteCommand(Command):
    """Command for marking a task as complete.

    Prompts for task ID, validates it exists, and marks
    the task as completed.
    """

    def __init__(self, storage: InMemoryStorage, console: Console) -> None:
        """Initialize MarkCompleteCommand.

        Args:
            storage: InMemoryStorage instance
            console: Rich Console instance
        """
        super().__init__(storage, console)

    def execute(self) -> None:
        """Execute the mark complete command.

        Prompts for task ID and marks the task as complete.
        Shows appropriate messages for success, already complete,
        or not found scenarios.
        """
        self.console.print("\n[bold cyan]Mark Task Complete[/bold cyan]")
        self.console.print("-" * 30)

        # Check if there are any tasks
        tasks = self.storage.get_all()
        if not tasks:
            self.console.print(
                "[bold blue]Info:[/bold blue] No tasks to complete. Add a task first!"
            )
            return

        # Get valid task ID
        task_id = self._get_valid_task_id()
        if task_id is None:
            return

        # Get the task
        task = self.storage.get(task_id)

        # Check if already completed
        if task.completed:
            self.console.print(
                f"[bold blue]Info:[/bold blue] Task #{task_id} is already completed."
            )
            return

        # Mark as complete
        self.storage.mark_complete(task_id)
        self.console.print()
        self.console.print(
            f"[bold green]Success![/bold green] Task #{task_id} marked as complete: {task.title}"
        )

    def _get_valid_task_id(self) -> int | None:
        """Get a valid task ID from user.

        Continues prompting until valid ID is entered.

        Returns:
            Valid task ID, or None if user cancels
        """
        while True:
            task_id_str = self._prompt_task_id()

            # Validate format
            try:
                task_id = int(task_id_str.strip())
            except (ValueError, AttributeError):
                self.console.print(
                    "[bold red]Error:[/bold red] Invalid input. Please enter a number."
                )
                continue

            # Validate task exists
            task = self.storage.get(task_id)
            if task is None:
                self.console.print(
                    f"[bold red]Error:[/bold red] Task #{task_id} not found."
                )
                continue

            return task_id

    def _prompt_task_id(self) -> str:
        """Prompt user for task ID.

        Returns:
            User's input for task ID
        """
        return Prompt.ask(
            "[bold]Enter Task ID[/bold]",
            console=self.console,
        )
