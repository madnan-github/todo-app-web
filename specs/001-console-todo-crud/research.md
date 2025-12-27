# Research: Console Todo CRUD Application

**Feature**: 001-console-todo-crud | **Date**: 2025-12-27

## Overview

This document captures research findings and decisions for the Phase I Console Todo CRUD implementation. All technology choices are pre-determined by the project constitution.

---

## Technology Decisions

### 1. Python 3.13+

**Decision**: Use Python 3.13+ as specified in constitution
**Rationale**:
- Modern Python with latest features
- Excellent ecosystem for CLI applications
- Strong type hinting support
- Constitution mandates this version

**Alternatives Considered**:
- Python 3.11/3.12 - Rejected: Constitution specifies 3.13+
- Other languages - Rejected: Constitution mandates Python for Phase I

---

### 2. UV Package Manager

**Decision**: Use UV for package management (not pip)
**Rationale**:
- Fast, modern Python package management
- Constitution mandates UV over pip
- Better dependency resolution
- Simpler pyproject.toml configuration

**Best Practices**:
- Initialize with `uv init`
- Add dependencies with `uv add <package>`
- Lock dependencies with `uv lock`
- Run commands with `uv run`

**Alternatives Considered**:
- pip + venv - Rejected: Constitution mandates UV
- poetry - Rejected: UV is faster and simpler

---

### 3. Rich Library for CLI

**Decision**: Use Rich for terminal output and user interaction
**Rationale**:
- Beautiful terminal output with colors
- Built-in Table component for task display
- Prompt.ask() for user input
- Constitution mandates Rich for Phase I

**Best Practices**:
- Use Console for colored output
- Use Table for displaying task lists
- Use Prompt.ask() for menu input
- Use Panel for styled messages
- Style errors in red, success in green

**Key Components**:
```python
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
```

**Alternatives Considered**:
- Click - Rejected: Better for arg parsing than menu-driven apps
- Textual - Rejected: Overkill for simple menu interface
- Plain print() - Rejected: Constitution mandates Rich

---

### 4. Pydantic for Data Validation

**Decision**: Use Pydantic BaseModel for Task entity
**Rationale**:
- Type-safe data validation
- Clear error messages for invalid input
- Constitution mandates Pydantic
- Integrates well with future SQLModel (Phase II)

**Best Practices**:
- Use Field() for validation constraints
- Use field_validator for custom business rules
- Define clear model with all required fields
- Handle ValidationError with user-friendly messages

**Key Patterns**:
```python
from pydantic import BaseModel, Field, field_validator

class Task(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = False
    created_at: datetime
    updated_at: datetime
```

**Alternatives Considered**:
- dataclasses - Rejected: Less validation support
- attrs - Rejected: Constitution mandates Pydantic
- Plain dict - Rejected: No type safety

---

### 5. In-Memory Storage

**Decision**: Use typed dictionary for in-memory storage
**Rationale**:
- Simplest solution for Phase I
- No external dependencies
- Constitution mandates no persistence in Phase I
- Easy to replace with database in Phase II

**Best Practices**:
- Use dict[int, Task] for O(1) lookups by ID
- Implement auto-incrementing ID counter
- Provide clear CRUD methods
- Return Optional[Task] for get operations

**Key Pattern**:
```python
class InMemoryStorage:
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> Task: ...
    def get(self, task_id: int) -> Optional[Task]: ...
    def get_all(self) -> list[Task]: ...
    def update(self, task_id: int, **kwargs) -> Optional[Task]: ...
    def delete(self, task_id: int) -> bool: ...
```

**Alternatives Considered**:
- SQLite - Rejected: Persistence not needed for Phase I
- JSON file - Rejected: Adds complexity for no benefit
- List - Rejected: O(n) lookups by ID

---

### 6. Command Pattern

**Decision**: Use Command pattern for operations
**Rationale**:
- Clean separation of concerns
- Each operation is self-contained
- Easy to add new commands
- Constitution skill recommends this pattern

**Best Practices**:
- Abstract base Command class with execute() method
- Concrete command for each operation
- Dependency injection for storage
- Commands handle their own input/output

**Key Pattern**:
```python
from abc import ABC, abstractmethod

class Command(ABC):
    def __init__(self, storage: InMemoryStorage, console: Console):
        self.storage = storage
        self.console = console

    @abstractmethod
    def execute(self) -> None: ...
```

**Alternatives Considered**:
- Single function per operation - Rejected: Less organized
- Strategy pattern - Rejected: Command is more appropriate for actions
- Direct implementation - Rejected: Harder to maintain

---

### 7. Testing with pytest

**Decision**: Use pytest for testing
**Rationale**:
- Standard Python testing framework
- Simple and readable test syntax
- Good fixtures support
- Works well with Pydantic models

**Best Practices**:
- Unit tests for Task model validation
- Unit tests for InMemoryStorage CRUD
- Integration tests for Command execution
- Use fixtures for storage setup
- Follow TDD: write tests first

**Test Structure**:
```
tests/
├── unit/
│   ├── test_task_model.py    # Pydantic validation tests
│   └── test_storage.py       # Storage CRUD tests
└── integration/
    └── test_commands.py      # Command execution tests
```

**Alternatives Considered**:
- unittest - Rejected: pytest is more Pythonic
- nose2 - Rejected: pytest is more popular

---

## Implementation Order

Based on research and dependencies:

1. **Project Setup** - pyproject.toml with UV
2. **Task Model** - Pydantic model with validation
3. **In-Memory Storage** - CRUD operations
4. **Command Base** - Abstract command class
5. **Individual Commands** - Add, View, Update, Delete, Complete
6. **CLI Menu** - Rich-based menu system
7. **Main Entry Point** - Application loop

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Rich not handling unicode | Low | Medium | Test with special characters early |
| Memory growth with many tasks | Low | Low | Phase I caps at ~100 tasks |
| Input validation edge cases | Medium | Low | Comprehensive Pydantic validators |

---

## References

- [Rich Documentation](https://rich.readthedocs.io/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [pytest Documentation](https://docs.pytest.org/)
