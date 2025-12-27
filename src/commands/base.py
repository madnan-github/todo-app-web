"""Abstract Command base class (T009).

This module defines the Command pattern interface for all operations.
Each command encapsulates a single operation with its dependencies.
"""

from abc import ABC, abstractmethod

from rich.console import Console

from src.storage.memory import InMemoryStorage


class Command(ABC):
    """Abstract base class for all commands.

    Commands follow the Command pattern, encapsulating operations
    with their dependencies (storage, console).

    Attributes:
        storage: The storage backend for task operations
        console: Rich console for output
    """

    def __init__(self, storage: InMemoryStorage, console: Console) -> None:
        """Initialize command with dependencies.

        Args:
            storage: InMemoryStorage instance for data operations
            console: Rich Console instance for terminal output
        """
        self.storage = storage
        self.console = console

    @abstractmethod
    def execute(self) -> None:
        """Execute the command.

        This method must be implemented by all concrete commands.
        It performs the command's operation and handles any output.
        """
        ...
