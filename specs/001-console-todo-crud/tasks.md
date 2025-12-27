# Tasks: Console Todo CRUD Application

**Input**: Design documents from `/specs/001-console-todo-crud/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: TDD is MANDATORY per constitution (Principle III). Tests MUST be written first and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md layout
- [x] T002 Initialize Python project with UV and create pyproject.toml with dependencies (rich, pydantic, pytest)
- [x] T003 [P] Create package markers (__init__.py) in src/, src/models/, src/storage/, src/commands/, src/cli/
- [x] T004 [P] Create test package markers (__init__.py) in tests/, tests/unit/, tests/integration/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Phase (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T005 [P] Unit tests for Task model validation in tests/unit/test_task_model.py
- [x] T006 [P] Unit tests for InMemoryStorage CRUD operations in tests/unit/test_storage.py

### Implementation for Foundational Phase

- [x] T007 Implement Task Pydantic model with validation in src/models/task.py (per data-model.md)
- [x] T008 Implement InMemoryStorage class with CRUD operations in src/storage/memory.py (per data-model.md)
- [x] T009 [P] Create abstract Command base class in src/commands/base.py (per research.md Command pattern)

**Checkpoint**: Foundation ready - Task model and storage validated. User story implementation can now begin.

---

## Phase 3: User Story 6 - Navigate Application Menu (Priority: P1) 🎯 MVP Foundation

**Goal**: Users can see and interact with the main menu to access all features

**Independent Test**: Run the application and verify menu displays numbered options and responds to selections

**Why First**: Menu is the entry point for ALL other user stories - must exist before any command can be tested

### Tests for User Story 6 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US6] Unit tests for menu display and input handling in tests/unit/test_menu.py
- [x] T011 [P] [US6] Integration test for menu navigation flow in tests/integration/test_menu_integration.py

### Implementation for User Story 6

- [x] T012 [US6] Implement Rich-based menu display in src/cli/menu.py (FR-001)
- [x] T013 [US6] Implement menu input validation and error handling in src/cli/menu.py (FR-008, FR-009)
- [x] T014 [US6] Implement main application loop in src/main.py
- [x] T015 [US6] Implement graceful exit with goodbye message in src/main.py (US6.4)

**Checkpoint**: Application launches with menu, accepts input, handles invalid options, and exits gracefully

---

## Phase 4: User Story 1 - Add a New Task (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with title and optional description

**Independent Test**: Select "Add task", enter details, verify task appears in list

### Tests for User Story 1 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US1] Unit tests for AddTaskCommand in tests/unit/test_add_command.py
- [x] T017 [P] [US1] Integration test for add task flow in tests/integration/test_add_integration.py

### Implementation for User Story 1

- [x] T018 [US1] Implement AddTaskCommand in src/commands/add.py (FR-002, FR-003, FR-005)
- [x] T019 [US1] Add title/description prompts with Rich in src/commands/add.py
- [x] T020 [US1] Add validation error display (empty title, length limits) in src/commands/add.py (FR-008, FR-009)
- [x] T021 [US1] Add success confirmation message in src/commands/add.py (FR-010)
- [x] T022 [US1] Wire AddTaskCommand to menu option 1 in src/main.py

**Checkpoint**: Can add tasks with validation, see confirmation, handle errors

---

## Phase 5: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can see all tasks in a formatted table

**Independent Test**: Add sample tasks, select "View tasks", verify formatted table shows all tasks

### Tests for User Story 2 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US2] Unit tests for ViewTasksCommand in tests/unit/test_view_command.py
- [x] T024 [P] [US2] Integration test for view tasks flow in tests/integration/test_view_integration.py

### Implementation for User Story 2

- [x] T025 [US2] Implement ViewTasksCommand in src/commands/view.py (FR-007)
- [x] T026 [US2] Implement Rich Table display with ID, Title, Status, Created columns in src/commands/view.py
- [x] T027 [US2] Add status indicators (✓ green for complete, ○ dim for pending) in src/commands/view.py
- [x] T028 [US2] Add "no tasks" friendly message when list is empty in src/commands/view.py
- [x] T029 [US2] Wire ViewTasksCommand to menu option 2 in src/main.py

**Checkpoint**: Can view all tasks in formatted table, see status indicators, see empty message

---

## Phase 6: User Story 3 - Mark Task as Complete (Priority: P1)

**Goal**: Users can mark a pending task as complete

**Independent Test**: Add a task, mark it complete by ID, verify status changes in task list

### Tests for User Story 3 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T030 [P] [US3] Unit tests for MarkCompleteCommand in tests/unit/test_complete_command.py
- [x] T031 [P] [US3] Integration test for mark complete flow in tests/integration/test_complete_integration.py

### Implementation for User Story 3

- [x] T032 [US3] Implement MarkCompleteCommand in src/commands/complete.py (FR-014)
- [x] T033 [US3] Add task ID prompt with validation in src/commands/complete.py (FR-008)
- [x] T034 [US3] Add "task not found" error handling in src/commands/complete.py (FR-015)
- [x] T035 [US3] Add "already completed" info message in src/commands/complete.py (US3.2)
- [x] T036 [US3] Add success confirmation message in src/commands/complete.py (FR-010)
- [x] T037 [US3] Wire MarkCompleteCommand to menu option 5 in src/main.py

**Checkpoint**: Can mark tasks complete, see confirmation, handle already-complete and not-found cases

---

## Phase 7: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Users can update title and/or description of existing tasks

**Independent Test**: Add a task, update its title/description, verify changes in task list

### Tests for User Story 4 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T038 [P] [US4] Unit tests for UpdateTaskCommand in tests/unit/test_update_command.py
- [x] T039 [P] [US4] Integration test for update task flow in tests/integration/test_update_integration.py

### Implementation for User Story 4

- [x] T040 [US4] Implement UpdateTaskCommand in src/commands/update.py (FR-012, FR-006)
- [x] T041 [US4] Add task ID prompt with validation in src/commands/update.py
- [x] T042 [US4] Add title/description update prompts (show current, allow skip) in src/commands/update.py
- [x] T043 [US4] Add validation for empty title on update in src/commands/update.py (US4.4)
- [x] T044 [US4] Add "task not found" error handling in src/commands/update.py (FR-015)
- [x] T045 [US4] Add success confirmation message in src/commands/update.py (FR-010)
- [x] T046 [US4] Wire UpdateTaskCommand to menu option 3 in src/main.py

**Checkpoint**: Can update task title/description, skip fields, handle validation and not-found errors

---

## Phase 8: User Story 5 - Delete a Task (Priority: P2)

**Goal**: Users can delete tasks they no longer need

**Independent Test**: Add a task, delete it by ID, verify it no longer appears in list

### Tests for User Story 5 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T047 [P] [US5] Unit tests for DeleteTaskCommand in tests/unit/test_delete_command.py
- [x] T048 [P] [US5] Integration test for delete task flow in tests/integration/test_delete_integration.py

### Implementation for User Story 5

- [x] T049 [US5] Implement DeleteTaskCommand in src/commands/delete.py (FR-013)
- [x] T050 [US5] Add task ID prompt with validation in src/commands/delete.py
- [x] T051 [US5] Add "task not found" error handling in src/commands/delete.py (FR-015)
- [x] T052 [US5] Add success confirmation message in src/commands/delete.py (FR-010)
- [x] T053 [US5] Wire DeleteTaskCommand to menu option 4 in src/main.py

**Checkpoint**: Can delete tasks, see confirmation, handle not-found errors, other tasks remain unchanged

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T054 [P] Add comprehensive edge case tests (special chars, unicode, length limits) in tests/unit/test_edge_cases.py
- [x] T055 [P] Add performance test for 100+ tasks in tests/integration/test_performance.py
- [x] T056 Code cleanup: ensure consistent error message styling (red for errors)
- [x] T057 Code cleanup: ensure consistent success message styling (green for confirmations)
- [x] T058 Run quickstart.md validation - verify all documented behaviors work
- [x] T059 Final manual testing of all 6 user stories end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US6 Menu (Phase 3)**: Depends on Foundational - BLOCKS other user stories (entry point)
- **User Stories 1-5 (Phase 4-8)**: Depend on US6 Menu completion
  - US1-US3 (P1 priority) should complete before US4-US5 (P2)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

```
Setup (P1) ──► Foundational (P2) ──► US6 Menu (P3)
                                         │
                                         ▼
                        ┌────────────────┼────────────────┐
                        │                │                │
                        ▼                ▼                ▼
                   US1 Add (P4)    US2 View (P5)    US3 Complete (P6)
                        │                │                │
                        └────────────────┼────────────────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                                 │
                        ▼                                 ▼
                   US4 Update (P7)                  US5 Delete (P8)
                        │                                 │
                        └────────────────┬────────────────┘
                                         │
                                         ▼
                                    Polish (P9)
```

### Within Each User Story (TDD Cycle)

1. Write tests FIRST → Verify they FAIL
2. Implement command class
3. Add prompts and validation
4. Add error/success messages
5. Wire to menu
6. Run tests → Verify they PASS
7. Story complete before moving to next

### Parallel Opportunities

**Phase 1 (Setup):**
- T003 and T004 can run in parallel (different directories)

**Phase 2 (Foundational):**
- T005 and T006 can run in parallel (different test files)
- T009 can run in parallel with T007/T008 (different file)

**Each User Story:**
- Test tasks within a story can run in parallel (T016+T017, T023+T024, etc.)

**After US6 Menu Complete:**
- US1, US2, US3 can theoretically run in parallel (different command files)
- However, for solo developer, recommend sequential P1 order

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD):
Task: "Unit tests for AddTaskCommand in tests/unit/test_add_command.py"
Task: "Integration test for add task flow in tests/integration/test_add_integration.py"

# After tests fail, implement sequentially (same file):
Task: "Implement AddTaskCommand in src/commands/add.py"
Task: "Add title/description prompts with Rich in src/commands/add.py"
...
```

---

## Implementation Strategy

### MVP First (US6 + US1 + US2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (Task model, Storage, Command base)
3. Complete Phase 3: US6 Menu (entry point for all features)
4. Complete Phase 4: US1 Add Task
5. Complete Phase 5: US2 View Tasks
6. **STOP and VALIDATE**: Can add and view tasks - minimal usable app!
7. Demo MVP if ready

### Incremental Delivery (P1 then P2)

1. MVP (US6 + US1 + US2) → Can add and view tasks
2. Add US3 Mark Complete → Can track progress
3. **P1 Complete** - All core functionality works
4. Add US4 Update → Can modify tasks
5. Add US5 Delete → Can remove tasks
6. **P2 Complete** - Full CRUD functionality
7. Polish phase → Production-ready

### Task Count Summary

| Phase | Tasks | Tests | Implementation |
|-------|-------|-------|----------------|
| Setup | 4 | 0 | 4 |
| Foundational | 5 | 2 | 3 |
| US6 Menu (P1) | 6 | 2 | 4 |
| US1 Add (P1) | 7 | 2 | 5 |
| US2 View (P1) | 7 | 2 | 5 |
| US3 Complete (P1) | 8 | 2 | 6 |
| US4 Update (P2) | 9 | 2 | 7 |
| US5 Delete (P2) | 7 | 2 | 5 |
| Polish | 6 | 2 | 4 |
| **Total** | **59** | **16** | **43** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD is mandatory**: Tests MUST fail before implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use `python-console-agent` for implementation as specified in constitution

---

## Implementation Complete

**Status**: ✅ ALL 59 TASKS COMPLETED

**Test Results**: 179 tests passing

**Implementation Date**: 2025-12-27
