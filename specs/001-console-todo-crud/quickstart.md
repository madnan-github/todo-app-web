# Quickstart: Console Todo CRUD Application

**Feature**: 001-console-todo-crud | **Date**: 2025-12-27

## Prerequisites

- Python 3.13+ installed
- UV package manager installed ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- Terminal with ANSI color support

## Setup

### 1. Initialize Project

```bash
# From repository root
uv init

# Add dependencies
uv add rich pydantic

# Add dev dependencies
uv add --dev pytest
```

### 2. Project Structure

After initialization, the project should have:

```
todo-app/
├── pyproject.toml      # UV package configuration
├── src/
│   ├── __init__.py
│   ├── main.py         # Entry point
│   ├── models/
│   │   └── task.py
│   ├── storage/
│   │   └── memory.py
│   ├── commands/
│   │   ├── base.py
│   │   ├── add.py
│   │   ├── view.py
│   │   ├── update.py
│   │   ├── delete.py
│   │   └── complete.py
│   └── cli/
│       └── menu.py
└── tests/
    ├── unit/
    └── integration/
```

## Running the Application

```bash
# Run the application
uv run python -m src.main

# Or with the entry point (after setup)
uv run todo
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/unit/test_task_model.py
```

## Expected Behavior

### Main Menu

When the application starts, you should see:

```
╭─────────────────────────────────────╮
│         📋 Todo Application         │
╰─────────────────────────────────────╯

What would you like to do?

  1. Add task
  2. View tasks
  3. Update task
  4. Delete task
  5. Mark complete
  6. Exit

Enter choice [1-6]:
```

### Adding a Task

```
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread

✅ Task #1 created: "Buy groceries"
```

### Viewing Tasks

```
┌────┬──────────────────────────────────────┬────────┬──────────────────┐
│ ID │ Title                                │ Status │ Created          │
├────┼──────────────────────────────────────┼────────┼──────────────────┤
│  1 │ Buy groceries                        │   ○    │ 2025-12-27 10:30 │
│  2 │ Review pull request                  │   ✓    │ 2025-12-27 11:00 │
└────┴──────────────────────────────────────┴────────┴──────────────────┘
```

### Marking Complete

```
Enter task ID to mark complete: 1

✅ Task #1 marked as complete!
```

### Error Handling

```
Enter task title:

❌ Error: Title cannot be empty

Enter task ID to mark complete: 999

❌ Error: Task #999 not found
```

## Development Workflow

### TDD Cycle

1. **Red**: Write a failing test for the feature
2. **Green**: Write minimal code to make it pass
3. **Refactor**: Clean up while tests still pass

```bash
# Example: Testing Task model
uv run pytest tests/unit/test_task_model.py -v

# Watch mode (if using pytest-watch)
uv run ptw tests/
```

### Code Style

```bash
# Format code
uv run ruff format src/ tests/

# Lint code
uv run ruff check src/ tests/
```

## Troubleshooting

### "Module not found" Error

Ensure you're running from the project root:
```bash
cd /path/to/todo-app
uv run python -m src.main
```

### Colors Not Showing

Check terminal ANSI support:
```bash
python -c "from rich.console import Console; Console().print('[green]Test[/green]')"
```

### UV Not Found

Install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Use `python-console-agent` for TDD implementation
3. Follow Red-Green-Refactor cycle
4. Create PHR after significant milestones
