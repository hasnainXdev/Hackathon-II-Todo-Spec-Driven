---

description: "Task list for Todo Console Application implementation"
---

# Tasks: Todo Console Application

**Input**: Design documents from `/specs/001-todo-console-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan in src/todo_app/
- [x] T002 Initialize Python project with dependencies in requirements.txt
- [x] T003 [P] Configure linting and formatting tools (pyproject.toml)
- [x] T004 Create initial README.md with project overview
- [x] T005 Create CLAUDE.md with Claude Code instructions
- [x] T006 Create pyproject.toml with project configuration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create base Task model in src/todo_app/models/task.py
- [x] T008 Create TaskService in src/todo_app/services/task_service.py
- [x] T009 [P] Create utility functions in src/todo_app/utils/helpers.py
- [x] T010 Setup in-memory storage structure in src/todo_app/services/task_service.py
- [x] T011 Create main application entry point in src/todo_app/main.py
- [x] T012 Setup error handling infrastructure in src/todo_app/utils/helpers.py
- [x] T013 Configure logging in src/todo_app/utils/helpers.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add New Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add new tasks with title and description to the todo list

**Independent Test**: Can be fully tested by adding a new task and verifying it appears in the task list, delivering the core value of task management.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T014 [P] [US1] Unit test for Task model validation in tests/unit/test_task.py
- [x] T015 [P] [US1] Unit test for TaskService.add_task method in tests/unit/test_task_service.py
- [x] T016 [P] [US1] Integration test for add task CLI command in tests/integration/test_cli.py

### Implementation for User Story 1

- [x] T017 [P] [US1] Implement Task model with validation in src/todo_app/models/task.py
- [x] T018 [US1] Implement TaskService.add_task method in src/todo_app/services/task_service.py
- [x] T019 [US1] Implement CLI command for adding tasks in src/todo_app/cli/main.py
- [x] T020 [US1] Add argument parsing for add command in src/todo_app/cli/main.py
- [x] T021 [US1] Add success/error messages for add task operation in src/todo_app/cli/main.py
- [x] T022 [US1] Add validation for required title field in src/todo_app/models/task.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Enable users to view all tasks with their status indicators

**Independent Test**: Can be fully tested by adding tasks and then viewing the list, delivering visibility into all tasks with their status.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US2] Unit test for TaskService.get_all_tasks method in tests/unit/test_task_service.py
- [x] T024 [P] [US2] Integration test for view tasks CLI command in tests/integration/test_cli.py

### Implementation for User Story 2

- [x] T025 [US2] Implement TaskService.get_all_tasks method in src/todo_app/services/task_service.py
- [x] T026 [US2] Implement CLI command for viewing tasks in src/todo_app/cli/main.py
- [x] T027 [US2] Add argument parsing for list/view command in src/todo_app/cli/main.py
- [x] T028 [US2] Format task display with ID, title, description, and completion status in src/todo_app/cli/main.py
- [x] T029 [US2] Handle empty task list case in src/todo_app/cli/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Tasks Complete/Incomplete (Priority: P2)

**Goal**: Enable users to mark tasks as complete or incomplete to track progress

**Independent Test**: Can be fully tested by marking tasks as complete/incomplete and verifying the status updates, delivering task status management functionality.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T030 [P] [US3] Unit test for TaskService.mark_complete method in tests/unit/test_task_service.py
- [x] T031 [P] [US3] Unit test for TaskService.mark_incomplete method in tests/unit/test_task_service.py
- [x] T032 [P] [US3] Integration test for mark complete CLI command in tests/integration/test_cli.py
- [x] T033 [P] [US3] Integration test for mark incomplete CLI command in tests/integration/test_cli.py

### Implementation for User Story 3

- [x] T034 [US3] Implement TaskService.mark_complete method in src/todo_app/services/task_service.py
- [x] T035 [US3] Implement TaskService.mark_incomplete method in src/todo_app/services/task_service.py
- [x] T036 [US3] Implement CLI command for marking tasks complete in src/todo_app/cli/main.py
- [x] T037 [US3] Implement CLI command for marking tasks incomplete in src/todo_app/cli/main.py
- [x] T038 [US3] Add argument parsing for complete/incomplete commands in src/todo_app/cli/main.py
- [x] T039 [US3] Add validation for valid task ID in src/todo_app/services/task_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Enable users to update the details of existing tasks to maintain accurate information

**Independent Test**: Can be fully tested by updating task details and verifying the changes persist, delivering task modification functionality.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T040 [P] [US4] Unit test for TaskService.update_task method in tests/unit/test_task_service.py
- [x] T041 [P] [US4] Integration test for update task CLI command in tests/integration/test_cli.py

### Implementation for User Story 4

- [x] T042 [US4] Implement TaskService.update_task method in src/todo_app/services/task_service.py
- [x] T043 [US4] Implement CLI command for updating tasks in src/todo_app/cli/main.py
- [x] T044 [US4] Add argument parsing for update command in src/todo_app/cli/main.py
- [x] T045 [US4] Add validation for valid task ID in src/todo_app/services/task_service.py
- [x] T046 [US4] Handle partial updates (title or description only) in src/todo_app/services/task_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: Enable users to delete tasks that they no longer need to keep the todo list clean

**Independent Test**: Can be fully tested by deleting tasks and verifying they are removed from the list, delivering task removal functionality.

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T047 [P] [US5] Unit test for TaskService.delete_task method in tests/unit/test_task_service.py
- [x] T048 [P] [US5] Integration test for delete task CLI command in tests/integration/test_cli.py

### Implementation for User Story 5

- [x] T049 [US5] Implement TaskService.delete_task method in src/todo_app/services/task_service.py
- [x] T050 [US5] Implement CLI command for deleting tasks in src/todo_app/cli/main.py
- [x] T051 [US5] Add argument parsing for delete command in src/todo_app/cli/main.py
- [x] T052 [US5] Add validation for valid task ID in src/todo_app/services/task_service.py
- [x] T053 [US5] Handle invalid task ID error in src/todo_app/cli/main.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T054 [P] Documentation updates in docs/setup.md
- [x] T055 Code cleanup and refactoring across all modules
- [x] T056 Performance optimization across all stories
- [x] T057 [P] Additional unit tests in tests/unit/
- [x] T058 Security hardening (input validation)
- [x] T059 Run quickstart.md validation
- [x] T060 Final integration testing of all features
- [x] T061 Update README.md with complete usage instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3/US4 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for Task model validation in tests/unit/test_task.py"
Task: "Unit test for TaskService.add_task method in tests/unit/test_task_service.py"
Task: "Integration test for add task CLI command in tests/integration/test_cli.py"

# Launch all implementation for User Story 1 together:
Task: "Implement Task model with validation in src/todo_app/models/task.py"
Task: "Implement TaskService.add_task method in src/todo_app/services/task_service.py"
Task: "Implement CLI command for adding tasks in src/todo_app/cli/main.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence