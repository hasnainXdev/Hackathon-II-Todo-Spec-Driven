# CLAUDE.md

## Claude Code Instructions for Todo Console Application

This document provides instructions for Claude when working on the Todo Console Application project.

### Project Overview

The Todo Console Application is a command-line application that allows users to manage their tasks. It stores tasks in memory only and provides functionality to add, view, update, delete, and mark tasks as complete/incomplete.

### Architecture

The application follows a clean architecture with the following components:

- **Models**: Task data structure and validation (in `src/todo_app/models/`)
- **Services**: Business logic for task management (in `src/todo_app/services/`)
- **CLI**: Command-line interface and user interaction (in `src/todo_app/cli/`)
- **Utils**: Helper functions and utilities (in `src/todo_app/utils/`)

### Key Technologies

- Python 3.13+
- argparse for command-line parsing
- pytest for testing
- UV for package management

### Task Entity

The Task entity has the following fields:
- `id` (int): Unique identifier for the task, auto-incremented
- `title` (str): Title of the task (required)
- `description` (str): Description of the task (optional, can be empty)
- `completed` (bool): Completion status of the task (default: False)

### Implementation Guidelines

1. Follow the separation of concerns as outlined in the architecture
2. Implement proper error handling with user-friendly messages
3. Write tests before implementation (TDD approach)
4. Follow Python best practices and PEP 8 style guide
5. Ensure the in-memory storage works correctly with auto-incrementing IDs
6. Validate user inputs appropriately

### CLI Commands

The application supports the following commands:
- `add`: Add a new task
- `list`/`view`: View all tasks
- `update`: Update an existing task
- `delete`: Delete a task by ID
- `complete`: Mark a task as complete
- `incomplete`: Mark a task as incomplete