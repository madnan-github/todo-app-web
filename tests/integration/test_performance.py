"""Performance tests for 100+ tasks (T055).

Tests that the application handles larger task lists efficiently.
"""

import pytest
import time
from io import StringIO

from rich.console import Console

from src.commands.view import ViewTasksCommand
from src.storage.memory import InMemoryStorage


class TestPerformanceWith100Tasks:
    """Performance tests with 100+ tasks."""

    def test_add_100_tasks_performance(self) -> None:
        """Adding 100 tasks completes in reasonable time."""
        storage = InMemoryStorage()

        start = time.time()
        for i in range(100):
            storage.add(
                title=f"Task number {i + 1}",
                description=f"Description for task {i + 1}" * 10
            )
        elapsed = time.time() - start

        assert len(storage) == 100
        # Should complete in under 1 second
        assert elapsed < 1.0, f"Adding 100 tasks took {elapsed:.2f}s"

    def test_get_all_100_tasks_performance(self) -> None:
        """Getting all 100 tasks completes quickly."""
        storage = InMemoryStorage()
        for i in range(100):
            storage.add(title=f"Task {i + 1}")

        start = time.time()
        tasks = storage.get_all()
        elapsed = time.time() - start

        assert len(tasks) == 100
        # Should complete in under 100ms
        assert elapsed < 0.1, f"Getting 100 tasks took {elapsed:.2f}s"

    def test_view_100_tasks_performance(self) -> None:
        """Viewing 100 tasks displays in under 1 second (SC-002)."""
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        storage = InMemoryStorage()

        # Add 100 tasks
        for i in range(100):
            storage.add(
                title=f"Task number {i + 1}",
                description=f"Description {i + 1}"
            )

        command = ViewTasksCommand(storage, console)

        start = time.time()
        command.execute()
        elapsed = time.time() - start

        # Per SC-002: Task list display <1 second
        assert elapsed < 1.0, f"Viewing 100 tasks took {elapsed:.2f}s"

        # Verify output contains tasks
        output_text = output.getvalue()
        assert "Task number 1" in output_text
        assert "Task number 100" in output_text

    def test_get_single_task_from_100_performance(self) -> None:
        """Getting a single task from 100 is fast (O(1))."""
        storage = InMemoryStorage()
        for i in range(100):
            storage.add(title=f"Task {i + 1}")

        start = time.time()
        # Get task in the middle
        task = storage.get(50)
        elapsed = time.time() - start

        assert task is not None
        assert task.id == 50
        # Should be nearly instant (dict lookup)
        assert elapsed < 0.01, f"Getting single task took {elapsed:.4f}s"


class TestPerformanceWith200Tasks:
    """Performance tests with 200 tasks (beyond minimum requirement)."""

    def test_storage_handles_200_tasks(self) -> None:
        """Storage handles 200 tasks without degradation."""
        storage = InMemoryStorage()

        start = time.time()
        for i in range(200):
            storage.add(title=f"Task {i + 1}")
        elapsed = time.time() - start

        assert len(storage) == 200
        # Should still be fast
        assert elapsed < 2.0

    def test_mixed_operations_performance(self) -> None:
        """Mixed CRUD operations are performant."""
        storage = InMemoryStorage()

        start = time.time()

        # Add 50 tasks
        for i in range(50):
            storage.add(title=f"Task {i + 1}")

        # Update 20 tasks
        for i in range(1, 21):
            storage.update(i, title=f"Updated Task {i}")

        # Mark 10 complete
        for i in range(1, 11):
            storage.mark_complete(i)

        # Delete 5 tasks
        for i in range(41, 46):
            storage.delete(i)

        # Get all
        tasks = storage.get_all()

        elapsed = time.time() - start

        assert len(tasks) == 45  # 50 - 5 deleted
        assert elapsed < 1.0
