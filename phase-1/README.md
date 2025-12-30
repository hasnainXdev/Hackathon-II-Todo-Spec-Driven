# Todo Console Application

A command-line todo application that stores tasks with persistent in-memory storage between CLI commands.

## Features

- Add new tasks with title and description
- View all tasks with their status indicators
- Mark tasks as complete/incomplete
- Update task details
- Delete tasks by ID
- Persistent storage that maintains tasks between CLI command executions

## Prerequisites

- Python 3.13 or higher
- UV package manager

## Setup

1. Navigate to the project directory:
   ```bash
   cd /path/to/hackathon-II-todo-spec-driven/phase-1
   ```

2. Install dependencies using UV:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

## Usage

1. Activate your virtual environment:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Run the application:
   ```bash
   # Using the module approach also here remove `PYTHONPATH=src`
   PYTHONPATH=src uv run python -m src.todo_app.cli.main --help

   # Or directly
   PYTHONPATH=src uv run python src/todo_app/cli/main.py --help
   ```

## Basic Commands (remove `PYTHONPATH=src` if it not installed from microsoft store)

- Add a task: `PYTHONPATH=src uv run python -m src.todo_app.cli.main add --title "My Task" --description "Task details"`
- View all tasks: `PYTHONPATH=src uv run python -m src.todo_app.cli.main list`
- Update a task: `PYTHONPATH=src uv run python -m src.todo_app.cli.main update --id 1 --title "Updated Task"`
- Mark complete: `PYTHONPATH=src uv run python -m src.todo_app.cli.main complete --id 1`
- Mark incomplete: `PYTHONPATH=src uv run python -m src.todo_app.cli.main incomplete --id 1`
- Delete a task: `PYTHONPATH=src uv run python -m src.todo_app.cli.main delete --id 1`

## Command Aliases

- `list` and `view` are equivalent for viewing tasks
- Short flags: `-t` for `--title`, `-d` for `--description`, `-i` for `--id`

## Storage

The application uses persistent in-memory storage that maintains tasks between CLI command executions. Tasks are stored in a temporary file and will persist until the application is reset or the file is manually deleted.

## Development

1. Install in development mode:
   ```bash
   uv pip install -e .
   ```

2. Run tests:
   ```bash
   uv run pytest
   ```

3. Run specific test:
   ```bash
   uv run pytest tests/unit/test_task.py
   ```

## Project Structure

```
src/
├── todo_app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # Task data model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py      # Task management logic
│   │   └── persistent_storage.py # Persistent in-memory storage
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py              # Command-line interface
│   └── utils/
│       ├── __init__.py
│       └── helpers.py           # Utility functions
tests/
├── unit/
│   ├── test_task.py             # Task model tests
│   └── test_task_service.py     # Task service tests
├── integration/
│   └── test_cli.py              # CLI integration tests
└── conftest.py                  # Test configuration
```