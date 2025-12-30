# Quickstart Guide: Todo Console Application

## Prerequisites
- Python 3.13 or higher
- UV package manager

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
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
   python -m src.main
   # or if installed as package:
   todo_app --help
   ```

## Basic Commands
- Add a task: `todo_app add --title "My Task" --description "Task details"`
- View all tasks: `todo_app list`
- Update a task: `todo_app update --id 1 --title "Updated Task"`
- Mark complete: `todo_app complete --id 1`
- Delete a task: `todo_app delete --id 1`

## Development
1. Install in development mode:
   ```bash
   uv pip install -e .
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Run specific test:
   ```bash
   pytest tests/unit/test_task.py
   ```