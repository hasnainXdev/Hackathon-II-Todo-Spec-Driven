from typing import Dict, Any
from datetime import datetime
from uuid import uuid4
import json
from .producer import get_kafka_producer, async_produce_event
from ..models.task import Task, Event


class EventPublisher:
    """Handles publishing events to Kafka topics."""

    def __init__(self):
        self.kafka_producer = get_kafka_producer()

    async def publish_task_created(self, task: Task, user_id: str):
        """Publish TASK_CREATED event to Kafka."""
        event_data = {
            "event_id": str(uuid4()),
            "event_type": "TASK_CREATED",
            "aggregate_id": str(task.id),
            "aggregate_type": "Task",
            "payload": {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "tags": task.tags,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": str(user_id),
                "created_at": task.created_at.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat(),
            "user_context": {"user_id": str(user_id)},
            "correlation_id": str(uuid4()),  # Could come from request context
            "causation_id": None,  # Would be set if this event is caused by another
            "version": 1,
            "source_service": "recurring-task-service"
        }

        await async_produce_event("task-events", event_data, key=str(task.id))
        print(f"Published TASK_CREATED event for task {task.id}")

    async def publish_task_updated(self, task: Task, user_id: str, updated_fields: list = None):
        """Publish TASK_UPDATED event to Kafka."""
        event_data = {
            "event_id": str(uuid4()),
            "event_type": "TASK_UPDATED",
            "aggregate_id": str(task.id),
            "aggregate_type": "Task",
            "payload": {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "tags": task.tags,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "updated_at": task.updated_at.isoformat(),
                "user_id": str(user_id),
                "updated_fields": updated_fields or []
            },
            "timestamp": datetime.utcnow().isoformat(),
            "user_context": {"user_id": str(user_id)},
            "correlation_id": str(uuid4()),  # Could come from request context
            "causation_id": None,  # Would be set if this event is caused by another
            "version": 1,
            "source_service": "recurring-task-service"
        }

        await async_produce_event("task-events", event_data, key=str(task.id))
        print(f"Published TASK_UPDATED event for task {task.id}")

    async def publish_task_completed(self, task: Task, user_id: str):
        """Publish TASK_COMPLETED event to Kafka."""
        event_data = {
            "event_id": str(uuid4()),
            "event_type": "TASK_COMPLETED",
            "aggregate_id": str(task.id),
            "aggregate_type": "Task",
            "payload": {
                "task_id": str(task.id),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "user_id": str(user_id)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "user_context": {"user_id": str(user_id)},
            "correlation_id": str(uuid4()),  # Could come from request context
            "causation_id": None,  # Would be set if this event is caused by another
            "version": 1,
            "source_service": "recurring-task-service"
        }

        await async_produce_event("task-events", event_data, key=str(task.id))
        print(f"Published TASK_COMPLETED event for task {task.id}")

    async def publish_recurring_task_created(self, original_task_id: str, new_task_id: str, user_id: str):
        """Publish RECURRING_TASK_CREATED event to Kafka."""
        event_data = {
            "event_id": str(uuid4()),
            "event_type": "RECURRING_TASK_CREATED",
            "aggregate_id": str(new_task_id),
            "aggregate_type": "Task",
            "payload": {
                "original_task_id": str(original_task_id),
                "new_task_id": str(new_task_id),
                "user_id": str(user_id)
            },
            "timestamp": datetime.utcnow().isoformat(),
            "user_context": {"user_id": str(user_id)},
            "correlation_id": str(uuid4()),
            "causation_id": None,
            "version": 1,
            "source_service": "recurring-task-service"
        }

        await async_produce_event("task-events", event_data, key=str(new_task_id))
        print(f"Published RECURRING_TASK_CREATED event for new task {new_task_id}")