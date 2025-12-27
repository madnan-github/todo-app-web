# Todo App

A console-based Todo CRUD application with a beautiful Rich CLI interface.

## Features

- Add tasks with title and optional description
- View all tasks in a formatted table
- Update task details (title and description)
- Delete tasks by ID
- Mark tasks as complete
- Beautiful terminal output with Rich library

## Requirements

- Python 3.13+
- UV package manager

## Setup

```bash
# Install dependencies
uv sync

# Install dev dependencies (for testing)
uv sync --all-extras
```

## Usage

```bash
# Run the application
uv run python -m src.main
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
```

## Project Structure

```
src/
├── __init__.py
├── main.py              # Application entry point
├── models/
│   ├── __init__.py
│   └── task.py          # Task Pydantic model
├── storage/
│   ├── __init__.py
│   └── memory.py        # In-memory storage
├── commands/
│   ├── __init__.py
│   ├── base.py          # Abstract Command base class
│   ├── add.py           # AddTaskCommand
│   ├── view.py          # ViewTasksCommand
│   ├── update.py        # UpdateTaskCommand
│   ├── delete.py        # DeleteTaskCommand
│   └── complete.py      # MarkCompleteCommand
└── cli/
    ├── __init__.py
    └── menu.py          # Rich-based menu system

tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_task_model.py
│   └── test_storage.py
└── integration/
    ├── __init__.py
    └── test_commands.py
```

## Tech Stack

- **Python 3.13+** - Modern Python features
- **UV** - Fast package management
- **Rich** - Beautiful terminal output
- **Pydantic** - Data validation
- **pytest** - Testing framework
