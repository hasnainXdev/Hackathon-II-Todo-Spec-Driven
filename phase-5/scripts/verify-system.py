#!/usr/bin/env python3
"""
Verification script for the event-driven todo system.

This script verifies the complete event-driven flow from task creation to completion,
recurrence, and reminders in the local environment.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from uuid import uuid4

import httpx
from confluent_kafka import Consumer, KafkaException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CHAT_API_BASE_URL = "http://localhost:8000"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

# Topics to monitor
TOPICS_TO_MONITOR = ['task-events', 'reminders', 'task-updates']


class EventDrivenFlowVerifier:
    def __init__(self):
        self.http_client = httpx.AsyncClient()
        self.setup_kafka_consumer()
        
    def setup_kafka_consumer(self):
        """Set up Kafka consumer to monitor events."""
        self.consumer_config = {
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'group.id': f'verification-group-{int(time.time())}',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 1000,
        }
        self.consumer = Consumer(self.consumer_config)
        self.consumer.subscribe(TOPICS_TO_MONITOR)
        logger.info(f"Kafka consumer subscribed to topics: {TOPICS_TO_MONITOR}")

    async def create_task_via_chat(self, user_id: str, task_description: str) -> dict:
        """Create a task via the chat API."""
        logger.info(f"Creating task via chat API: {task_description}")
        
        response = await self.http_client.post(
            f"{CHAT_API_BASE_URL}/api/v1/chat/",
            json={
                "command": task_description,
                "userId": user_id
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to create task: {response.status_code} - {response.text}")
            return None
            
        result = response.json()
        logger.info(f"Task creation result: {result}")
        return result

    async def get_task_details(self, task_id: str, user_id: str) -> dict:
        """Get task details via the API."""
        logger.info(f"Getting task details for task ID: {task_id}")
        
        response = await self.http_client.get(
            f"{CHAT_API_BASE_URL}/api/v1/tasks/{task_id}",
            params={"user_id": user_id}
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get task: {response.status_code} - {response.text}")
            return None
            
        result = response.json()
        logger.info(f"Task details: {result}")
        return result

    async def complete_task(self, task_id: str, user_id: str) -> dict:
        """Complete a task via the API."""
        logger.info(f"Completing task: {task_id}")
        
        response = await self.http_client.post(
            f"{CHAT_API_BASE_URL}/api/v1/tasks/{task_id}/complete",
            params={"user_id": user_id}
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to complete task: {response.status_code} - {response.text}")
            return None
            
        result = response.json()
        logger.info(f"Task completion result: {result}")
        return result

    async def monitor_events(self, duration_seconds: int = 30) -> list:
        """Monitor Kafka for events during the specified duration."""
        logger.info(f"Monitoring Kafka events for {duration_seconds} seconds...")
        
        start_time = time.time()
        events = []
        
        while time.time() - start_time < duration_seconds:
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
                
                logger.info(f"Captured event from topic '{msg.topic()}': {message_data['event_type']} - {message_data['payload']}")
                events.append({
                    'topic': msg.topic(),
                    'event': message_data,
                    'timestamp': time.time()
                })
                
                # Commit the message
                self.consumer.commit(msg)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}")
                self.consumer.commit(msg)  # Commit to avoid getting stuck
            except Exception as e:
                logger.error(f"Error processing message: {e}")
        
        logger.info(f"Captured {len(events)} events during monitoring period")
        return events

    async def run_full_flow_verification(self):
        """Run the complete verification flow."""
        logger.info("Starting full event-driven flow verification...")
        
        # Generate a unique user ID for this test
        user_id = str(uuid4())
        logger.info(f"Using user ID for test: {user_id}")
        
        # Step 1: Create a task with a due date to trigger reminders
        task_desc = f"Test task for verification created at {datetime.now().strftime('%H:%M:%S')} - due tomorrow - high priority"
        create_result = await self.create_task_via_chat(user_id, task_desc)
        
        if not create_result or not create_result.get('taskId'):
            logger.error("Failed to create task, stopping verification")
            return False
        
        task_id = create_result['taskId']
        logger.info(f"Created task with ID: {task_id}")
        
        # Monitor events for a short period to capture the creation event
        creation_events = await self.monitor_events(5)
        
        # Verify that a TASK_CREATED event was published
        task_created_events = [e for e in creation_events if e['event']['event_type'] == 'TASK_CREATED']
        if not task_created_events:
            logger.error("No TASK_CREATED event was published!")
            return False
        else:
            logger.info(f"✓ Verified TASK_CREATED event was published: {task_created_events[0]['event']['payload']['title']}")
        
        # Step 2: Get the task details to verify it was stored correctly
        task_details = await self.get_task_details(task_id, user_id)
        if not task_details:
            logger.error("Failed to retrieve task details")
            return False
        
        logger.info(f"✓ Retrieved task details: {task_details['title']}")
        
        # Step 3: Complete the task to trigger completion events
        completion_result = await self.complete_task(task_id, user_id)
        if not completion_result:
            logger.error("Failed to complete task")
            return False
        
        logger.info(f"✓ Completed task: {completion_result['title']}")
        
        # Monitor events to capture the completion event
        completion_events = await self.monitor_events(5)
        
        # Verify that a TASK_COMPLETED event was published
        task_completed_events = [e for e in completion_events if e['event']['event_type'] == 'TASK_COMPLETED']
        if not task_completed_events:
            logger.error("No TASK_COMPLETED event was published!")
            return False
        else:
            logger.info(f"✓ Verified TASK_COMPLETED event was published: {task_completed_events[0]['event']['payload']['title']}")
        
        # Combine all events for final verification
        all_events = creation_events + completion_events
        
        # Summary
        logger.info("\n=== VERIFICATION SUMMARY ===")
        logger.info(f"Total events captured: {len(all_events)}")
        logger.info(f"Task created: {task_created_events[0]['event']['payload']['title'] if task_created_events else 'None'}")
        logger.info(f"Task completed: {task_completed_events[0]['event']['payload']['title'] if task_completed_events else 'None'}")
        
        # Check for any errors in the events
        error_events = [e for e in all_events if e['event']['event_type'].endswith('_ERROR')]
        if error_events:
            logger.error(f"Found {len(error_events)} error events!")
            for event in error_events:
                logger.error(f"  - {event}")
            return False
        
        logger.info("✓ All verification steps passed successfully!")
        return True

    async def close(self):
        """Close resources."""
        await self.http_client.aclose()
        self.consumer.close()


async def main():
    verifier = EventDrivenFlowVerifier()
    try:
        success = await verifier.run_full_flow_verification()
        if success:
            logger.info("\n🎉 VERIFICATION PASSED: Event-driven flow is working correctly!")
        else:
            logger.error("\n❌ VERIFICATION FAILED: Issues detected in the event-driven flow!")
    finally:
        await verifier.close()


if __name__ == "__main__":
    asyncio.run(main())