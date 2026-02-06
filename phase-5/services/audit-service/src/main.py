from confluent_kafka import Consumer, KafkaException
import json
import logging
from datetime import datetime
from sqlmodel import SQLModel, Field, create_engine, Session, select
from uuid import UUID, uuid4
from typing import Optional, List

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'chat-api'))

# Import the Event model from the chat-api service
from src.models.task import Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "audit-group"):
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 1000,
        }
        self.consumer = Consumer(self.consumer_config)

    def subscribe_to_all_task_events(self):
        """Subscribe to all task-related topics to audit all changes."""
        self.consumer.subscribe(['task-events', 'reminders', 'task-updates'])
        logger.info("Audit service subscribed to task-related topics")

    def process_event(self, message_data: dict):
        """Process an incoming event and store it in the audit log."""
        try:
            # Create an Event record from the message data
            event_record = Event(
                event_id=message_data.get('event_id'),
                event_type=message_data.get('event_type'),
                aggregate_id=message_data.get('aggregate_id'),
                aggregate_type=message_data.get('aggregate_type'),
                payload=message_data.get('payload', {}),
                timestamp=datetime.fromisoformat(message_data.get('timestamp')) if message_data.get('timestamp') else datetime.utcnow(),
                user_context=message_data.get('user_context', {}),
                correlation_id=message_data.get('correlation_id'),
                causation_id=message_data.get('causation_id'),
                version=message_data.get('version', 1),
                source_service=message_data.get('source_service', 'unknown')
            )
            
            # Save the event to the audit log (in a real system, this would be a database)
            self.save_audit_record(event_record)
            
            logger.info(f"Audited event: {event_record.event_type} for aggregate {event_record.aggregate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing audit event: {e}")
            return False

    def save_audit_record(self, event: Event):
        """Save the audit record to storage (placeholder implementation)."""
        # In a real implementation, you would save this to a database
        # For this example, we'll just log the event
        logger.info(f"Audit record saved: {event.event_type} - {event.aggregate_id}")

    def get_task_history(self, task_id: str) -> List[Event]:
        """Retrieve the history of events for a specific task (placeholder implementation)."""
        # In a real implementation, you would query the database for events
        # related to the specific task_id
        logger.info(f"Retrieving history for task {task_id}")
        # Placeholder: return an empty list
        return []

    def start_listening(self):
        """Start listening for events to audit."""
        logger.info("Audit service starting to listen for events...")
        
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
                    
                    # Process the event
                    self.process_event(message_data)
                    
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
            logger.info("Audit service interrupted by user")
        finally:
            self.consumer.close()


# For testing purposes
if __name__ == "__main__":
    service = AuditService()
    service.subscribe_to_all_task_events()
    service.start_listening()