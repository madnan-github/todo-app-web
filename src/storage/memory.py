"""In-memory storage for tasks (T008).

This module provides in-memory CRUD operations for Task entities.
Tasks are stored in a dictionary with auto-incrementing IDs.
"""

from datetime import datetime

from src.models.task import Task


class InMemoryStorage:
    """In-memory task storage with CRUD operations.

    Provides basic Create, Read, Update, Delete operations for tasks.
    Tasks are stored in memory and lost when the application exits.

    Attributes:
        _tasks: Dictionary storing tasks by ID
        _next_id: Counter for auto-incrementing task IDs
    """

    def __init__(self) -> None:
        """Initialize empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Create a new task with auto-generated ID and timestamps.

        Args:
            title: Task title (required, 1-200 chars)
            description: Task description (optional, max 1000 chars)

        Returns:
            The created Task with assigned ID and timestamps
        """
        now = datetime.now()
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            completed=False,
            created_at=now,
            updated_at=now,
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: The task ID to retrieve

        Returns:
            The Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Get all tasks, ordered by creation date (newest first).

        Returns:
            List of all tasks, newest first
        """
        tasks = list(self._tasks.values())
        # Sort by created_at descending (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> Task | None:
        """Update task fields.

        Args:
            task_id: The task ID to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            The updated Task if found, None otherwise
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None

        # Build update data
        update_data: dict[str, str | datetime] = {
            "updated_at": datetime.now(),
        }
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description

        # Create updated task using model_copy
        updated_task = task.model_copy(update=update_data)
        self._tasks[task_id] = updated_task
        return updated_task

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task ID to delete

        Returns:
            True if deleted, False if not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def mark_complete(self, task_id: int) -> Task | None:
        """Mark a task as complete.

        Args:
            task_id: The task ID to mark complete

        Returns:
            The updated Task if found, None otherwise
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None

        updated_task = task.model_copy(
            update={
                "completed": True,
                "updated_at": datetime.now(),
            }
        )
        self._tasks[task_id] = updated_task
        return updated_task

    def __len__(self) -> int:
        """Return the number of tasks in storage."""
        return len(self._tasks)

    def __iter__(self):
        """Iterate over all tasks."""
        return iter(self._tasks.values())
