"""UpdateTaskCommand implementation (T040-T046).

This module implements the Update Task command for modifying tasks.
"""

from rich.console import Console
from rich.prompt import Prompt

from src.commands.base import Command
from src.storage.memory import InMemoryStorage


class UpdateTaskCommand(Command):
    """Command for updating an existing task.

    Prompts for task ID, shows current values, and allows
    updating title and/or description. Empty input keeps original.
    """

    TITLE_MAX_LENGTH = 200
    DESCRIPTION_MAX_LENGTH = 1000

    def __init__(self, storage: InMemoryStorage, console: Console) -> None:
        """Initialize UpdateTaskCommand.

        Args:
            storage: InMemoryStorage instance
            console: Rich Console instance
        """
        super().__init__(storage, console)

    def execute(self) -> None:
        """Execute the update task command.

        Prompts for task ID, shows current values, and updates
        the task with new values. Empty input preserves original.
        """
        self.console.print("\n[bold cyan]Update Task[/bold cyan]")
        self.console.print("-" * 30)

        # Check if there are any tasks
        tasks = self.storage.get_all()
        if not tasks:
            self.console.print(
                "[bold blue]Info:[/bold blue] No tasks to update. Add a task first!"
            )
            return

        # Get valid task ID
        task_id = self._get_valid_task_id()
        if task_id is None:
            return

        # Get the task
        task = self.storage.get(task_id)

        # Show current values
        self.console.print()
        self.console.print(f"[dim]Current title:[/dim] {task.title}")
        self.console.print(f"[dim]Current description:[/dim] {task.description or '(empty)'}")
        self.console.print()
        self.console.print("[dim]Press Enter to keep current value[/dim]")

        # Get new values
        new_title = self._prompt_new_title()
        new_description = self._prompt_new_description()

        # Validate new title if provided
        if new_title:
            if len(new_title.strip()) > self.TITLE_MAX_LENGTH:
                self.console.print(
                    f"[bold red]Error:[/bold red] Title must be {self.TITLE_MAX_LENGTH} characters or less."
                )
                return

        # Validate new description if provided
        if new_description and len(new_description.strip()) > self.DESCRIPTION_MAX_LENGTH:
            self.console.print(
                f"[bold red]Error:[/bold red] Description must be {self.DESCRIPTION_MAX_LENGTH} characters or less."
            )
            return

        # Check if anything changed
        if not new_title and not new_description:
            self.console.print(
                "[bold blue]Info:[/bold blue] No changes made."
            )
            return

        # Perform update
        updated_task = self.storage.update(
            task_id,
            title=new_title.strip() if new_title else None,
            description=new_description.strip() if new_description else None,
        )

        self.console.print()
        self.console.print(
            f"[bold green]Success![/bold green] Task #{task_id} updated: {updated_task.title}"
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

    def _prompt_new_title(self) -> str:
        """Prompt user for new title.

        Returns:
            New title or empty string to skip
        """
        return Prompt.ask(
            "[bold]New title[/bold]",
            console=self.console,
            default="",
        )

    def _prompt_new_description(self) -> str:
        """Prompt user for new description.

        Returns:
            New description or empty string to skip
        """
        return Prompt.ask(
            "[bold]New description[/bold]",
            console=self.console,
            default="",
        )
