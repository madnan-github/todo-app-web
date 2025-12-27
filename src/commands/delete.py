"""DeleteTaskCommand implementation (T049-T053).

This module implements the Delete Task command for removing tasks.
"""

from rich.console import Console
from rich.prompt import Prompt

from src.commands.base import Command
from src.storage.memory import InMemoryStorage


class DeleteTaskCommand(Command):
    """Command for deleting a task.

    Prompts for task ID, validates it exists, and deletes
    the task from storage.
    """

    def __init__(self, storage: InMemoryStorage, console: Console) -> None:
        """Initialize DeleteTaskCommand.

        Args:
            storage: InMemoryStorage instance
            console: Rich Console instance
        """
        super().__init__(storage, console)

    def execute(self) -> None:
        """Execute the delete task command.

        Prompts for task ID and deletes the task.
        Shows success or error messages appropriately.
        """
        self.console.print("\n[bold cyan]Delete Task[/bold cyan]")
        self.console.print("-" * 30)

        # Check if there are any tasks
        tasks = self.storage.get_all()
        if not tasks:
            self.console.print(
                "[bold blue]Info:[/bold blue] No tasks to delete. Add a task first!"
            )
            return

        # Get valid task ID
        task_id = self._get_valid_task_id()
        if task_id is None:
            return

        # Get task info before deletion for confirmation message
        task = self.storage.get(task_id)
        task_title = task.title

        # Delete the task
        self.storage.delete(task_id)

        self.console.print()
        self.console.print(
            f"[bold green]Success![/bold green] Task #{task_id} deleted: {task_title}"
        )

    def _get_valid_task_id(self) -> int | None:
        """Get a valid task ID from user.

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
