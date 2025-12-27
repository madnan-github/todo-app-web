"""Main application entry point (T014-T015).

This module provides the main entry point for the Todo application.
Run with: uv run python -m src.main
"""

from rich.console import Console

from src.cli.menu import Menu
from src.commands.add import AddTaskCommand
from src.commands.complete import MarkCompleteCommand
from src.commands.delete import DeleteTaskCommand
from src.commands.update import UpdateTaskCommand
from src.commands.view import ViewTasksCommand
from src.storage.memory import InMemoryStorage


def main() -> None:
    """Run the Todo application.

    Initializes storage, menu, and command handlers.
    Runs the main menu loop until exit.
    """
    # Initialize components
    console = Console()
    storage = InMemoryStorage()
    menu = Menu(console=console)

    # Register command handlers
    menu.register_handler(1, AddTaskCommand(storage, console).execute)
    menu.register_handler(2, ViewTasksCommand(storage, console).execute)
    menu.register_handler(3, UpdateTaskCommand(storage, console).execute)
    menu.register_handler(4, DeleteTaskCommand(storage, console).execute)
    menu.register_handler(5, MarkCompleteCommand(storage, console).execute)

    # Run the application
    console.clear()
    menu.run_loop()


if __name__ == "__main__":
    main()
