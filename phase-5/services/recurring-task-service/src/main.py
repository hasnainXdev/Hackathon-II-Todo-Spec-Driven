from confluent_kafka import Consumer, KafkaException
import json
import logging
from datetime import datetime, timedelta
from sqlmodel import Session, select
from uuid import uuid4

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'chat-api'))

from src.models.task import Task, PriorityEnum
from src.database.init import get_db_session
from src.kafka.producer import get_kafka_producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecurringTaskService:
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "recurring-task-group"):
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 1000,
        }
        self.consumer = Consumer(self.consumer_config)
        self.kafka_producer = get_kafka_producer(bootstrap_servers)

    def subscribe_to_task_completion_topic(self):
        """Subscribe to the task-completion topic to detect completed recurring tasks."""
        self.consumer.subscribe(['task-events'])
        logger.info("Recurring task service subscribed to 'task-events' topic")

    def process_task_completed_event(self, message_data: dict):
        """Process a task completed event to check if it was recurring."""
        try:
            event_type = message_data.get('event_type')
            
            # Only process TASK_COMPLETED events
            if event_type != 'TASK_COMPLETED':
                return False
            
            task_payload = message_data.get('payload', {})
            task_id = task_payload.get('task_id')
            user_id = task_payload.get('user_id')
            
            # Get the original task to check if it was recurring
            with get_db_session() as session:
                statement = select(Task).where(Task.id == task_id)
                original_task = session.exec(statement).first()
                
                if not original_task or not original_task.recurrence_rule:
                    # Not a recurring task, nothing to do
                    return False
                
                # Create the next recurring task based on the recurrence rule
                next_task = self.create_next_recurring_task(original_task)
                
                if next_task:
                    # Publish a TASK_CREATED event for the new recurring task
                    self.publish_task_created_event(next_task, user_id)
                    logger.info(f"Created next recurring task from original task {task_id}")
                    return True
                else:
                    logger.warning(f"Could not create next recurring task from {task_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error processing task completed event: {e}")
            return False

    def create_next_recurring_task(self, original_task: Task) -> Task:
        """Create the next recurring task based on the recurrence rule."""
        try:
            # Parse the recurrence rule and calculate the next due date
            next_due_date = self.calculate_next_occurrence(
                original_task.due_date, 
                original_task.recurrence_rule
            )
            
            # Create a new task with the same properties as the original
            new_task = Task(
                title=original_task.title,
                description=original_task.description,
                priority=original_task.priority,
                tags=original_task.tags,
                due_date=next_due_date,
                recurrence_rule=original_task.recurrence_rule,  # Preserve the recurrence rule
                user_id=original_task.user_id,
                completed=False,
                completed_at=None
            )
            
            # Save the new task to the database
            with get_db_session() as session:
                session.add(new_task)
                session.commit()
                session.refresh(new_task)
            
            logger.info(f"Created new recurring task: {new_task.title}")
            return new_task
            
        except Exception as e:
            logger.error(f"Error creating next recurring task: {e}")
            return None

    def calculate_next_occurrence(self, last_due_date: datetime, recurrence_rule: str) -> datetime:
        """Calculate the next occurrence based on the recurrence rule."""
        if not last_due_date:
            last_due_date = datetime.utcnow()
        
        if recurrence_rule == 'daily':
            return last_due_date + timedelta(days=1)
        elif recurrence_rule == 'weekly':
            return last_due_date + timedelta(weeks=1)
        elif recurrence_rule == 'monthly':
            # Simple monthly calculation (adding ~30 days)
            return last_due_date + timedelta(days=30)
        elif recurrence_rule == 'yearly':
            return last_due_date + timedelta(days=365)
        else:
            # For more complex rules, you might want to implement custom logic
            logger.warning(f"Unknown recurrence rule: {recurrence_rule}, defaulting to daily")
            return last_due_date + timedelta(days=1)

    def publish_task_created_event(self, task: Task, user_id: str):
        """Publish a TASK_CREATED event for the new recurring task."""
        from src.kafka.publishers import EventPublisher
        event_publisher = EventPublisher()

        import asyncio
        asyncio.create_task(event_publisher.publish_task_created(task, user_id))

    def start_listening(self):
        """Start listening for task completion events."""
        logger.info("Recurring task service starting to listen for events...")
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        continue
                
                try:
                    # Decode the message
                    message_value = msg.value().decode('utf-8')
                    message_data = json.loads(message_value)
                    
                    # Process the task completed event
                    self.process_task_completed_event(message_data)
                    
                    # Commit the message
                    self.consumer.commit(msg)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON: {e}")
                    self.consumer.commit(msg)  # Commit to avoid getting stuck
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Don't commit on error to allow retry (in a real system you might want
                    # more sophisticated error handling like dead letter queues)
        
        except KeyboardInterrupt:
            logger.info("Recurring task service interrupted by user")
        finally:
            self.consumer.close()


# For testing purposes
if __name__ == "__main__":
    service = RecurringTaskService()
    service.subscribe_to_task_completion_topic()
    service.start_listening()