"""
Command-line interface for the Todo Console Application.
"""
import argparse
import sys
from typing import List
from todo_app.services.task_service import TaskService
from todo_app.utils.helpers import format_task


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Todo Console Application - Manage your tasks from the command line"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("--title", "-t", required=True, help="Title of the task")
    add_parser.add_argument("--description", "-d", default="", help="Description of the task")

    # List command
    list_parser = subparsers.add_parser("list", aliases=["view"], help="View all tasks")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("--id", "-i", required=True, type=int, help="ID of the task to update")
    update_parser.add_argument("--title", "-t", help="New title for the task")
    update_parser.add_argument("--description", "-d", help="New description for the task")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("--id", "-i", required=True, type=int, help="ID of the task to delete")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("--id", "-i", required=True, type=int, help="ID of the task to mark complete")

    # Incomplete command
    incomplete_parser = subparsers.add_parser("incomplete", help="Mark a task as incomplete")
    incomplete_parser.add_argument("--id", "-i", required=True, type=int, help="ID of the task to mark incomplete")

    return parser


def handle_add_command(task_service: TaskService, args) -> None:
    """Handle the add command."""
    try:
        task = task_service.add_task(args.title, args.description)
        print(f"Task added successfully with ID: {task.id}")
    except ValueError as e:
        print(f"Error adding task: {e}", file=sys.stderr)
        sys.exit(1)


def handle_list_command(task_service: TaskService, args) -> None:
    """Handle the list command."""
    tasks = task_service.get_all_tasks()
    if not tasks:
        print("No tasks found.")
        return
    
    for task in tasks:
        print(format_task(task))


def handle_update_command(task_service: TaskService, args) -> None:
    """Handle the update command."""
    try:
        # Check if at least one field to update is provided
        if args.title is None and args.description is None:
            print("Error: Please provide at least one field to update (--title or --description)", file=sys.stderr)
            sys.exit(1)
        
        updated_task = task_service.update_task(args.id, args.title, args.description)
        if updated_task:
            print(f"Task {args.id} updated successfully")
        else:
            print(f"Error: Task with ID {args.id} not found", file=sys.stderr)
            sys.exit(1)
    except ValueError as e:
        print(f"Error updating task: {e}", file=sys.stderr)
        sys.exit(1)


def handle_delete_command(task_service: TaskService, args) -> None:
    """Handle the delete command."""
    success = task_service.delete_task(args.id)
    if success:
        print(f"Task {args.id} deleted successfully")
    else:
        print(f"Error: Task with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)


def handle_complete_command(task_service: TaskService, args) -> None:
    """Handle the complete command."""
    success = task_service.mark_complete(args.id)
    if success:
        print(f"Task {args.id} marked as complete")
    else:
        print(f"Error: Task with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)


def handle_incomplete_command(task_service: TaskService, args) -> None:
    """Handle the incomplete command."""
    success = task_service.mark_incomplete(args.id)
    if success:
        print(f"Task {args.id} marked as incomplete")
    else:
        print(f"Error: Task with ID {args.id} not found", file=sys.stderr)
        sys.exit(1)


def main(args_list: List[str] = None) -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    
    if args_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args_list)
    
    # Create a task service instance
    task_service = TaskService()
    
    # Dispatch to the appropriate handler based on the command
    if args.command == "add":
        handle_add_command(task_service, args)
    elif args.command in ("list", "view"):
        handle_list_command(task_service, args)
    elif args.command == "update":
        handle_update_command(task_service, args)
    elif args.command == "delete":
        handle_delete_command(task_service, args)
    elif args.command == "complete":
        handle_complete_command(task_service, args)
    elif args.command == "incomplete":
        handle_incomplete_command(task_service, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()