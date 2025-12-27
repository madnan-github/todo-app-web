"""ViewTasksCommand implementation (T025-T029).

This module implements the View Tasks command for displaying all tasks.
"""

from rich.console import Console
from rich.table import Table
from rich.text import Text

from src.commands.base import Command
from src.storage.memory import InMemoryStorage


class ViewTasksCommand(Command):
    """Command for viewing all tasks.

    Displays all tasks in a formatted Rich table with
    ID, Title, Status, and Created date columns.
    """

    # Status indicators
    STATUS_COMPLETE = "[green]✓[/green]"
    STATUS_PENDING = "[dim]○[/dim]"

    def __init__(self, storage: InMemoryStorage, console: Console) -> None:
        """Initialize ViewTasksCommand.

        Args:
            storage: InMemoryStorage instance
            console: Rich Console instance
        """
        super().__init__(storage, console)

    def execute(self) -> None:
        """Execute the view tasks command.

        Displays all tasks in a formatted table.
        Shows friendly message if no tasks exist.
        """
        self.console.print("\n[bold cyan]Task List[/bold cyan]")
        self.console.print("-" * 30)

        tasks = self.storage.get_all()

        if not tasks:
            self._show_empty_message()
            return

        self._display_table(tasks)

    def _show_empty_message(self) -> None:
        """Display message when no tasks exist."""
        self.console.print()
        self.console.print(
            "[bold blue]Info:[/bold blue] No tasks yet. Use option 1 to add a task!"
        )

    def _display_table(self, tasks: list) -> None:
        """Display tasks in a Rich table.

        Args:
            tasks: List of Task objects to display
        """
        table = Table(show_header=True, header_style="bold cyan")

        # Add columns
        table.add_column("ID", style="dim", justify="right", width=5)
        table.add_column("Title", style="white", min_width=20, max_width=40)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Created", style="dim", width=16)

        # Add rows
        for task in tasks:
            status = self.STATUS_COMPLETE if task.completed else self.STATUS_PENDING
            created = task.created_at.strftime("%Y-%m-%d %H:%M")

            # Truncate long titles
            title = task.title
            if len(title) > 40:
                title = title[:37] + "..."

            table.add_row(
                str(task.id),
                title,
                status,
                created,
            )

        self.console.print()
        self.console.print(table)
        self.console.print()
        self.console.print(f"[dim]Total: {len(tasks)} task(s)[/dim]")
