from confluent_kafka import Consumer, KafkaException
import json
import logging
from typing import Callable, Dict, Any
import asyncio
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "default-group"):
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',  # Start from beginning if no committed offsets
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 1000,
            'session.timeout.ms': 60000,  # 60 seconds
            'max.poll.interval.ms': 300000,  # 5 minutes for long processing
            'heartbeat.interval.ms': 3000,
            'fetch.min.bytes': 1024,
            'fetch.wait.max.ms': 500
        }
        self.consumer = Consumer(self.consumer_config)
        self.running = False

    def subscribe_to_topics(self, topics: list):
        """Subscribe to the specified Kafka topics."""
        self.consumer.subscribe(topics)
        logger.info(f"Subscribed to topics: {topics}")

    def consume_messages(self, message_handler: Callable[[Dict[str, Any]], None], max_messages: int = None):
        """
        Consume messages from subscribed topics and process them with the handler.
        
        Args:
            message_handler: Function to handle incoming messages
            max_messages: Maximum number of messages to process (None for infinite)
        """
        msg_count = 0
        self.running = True
        
        try:
            while self.running:
                # Poll for messages with a timeout of 1 second
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    # Check if this is an end-of-partition event
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        logger.debug(f'Reached end of partition: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')
                    else:
                        logger.error(f'Error while consuming message: {msg.error()}')
                    continue
                
                try:
                    # Decode the message value
                    message_value = msg.value().decode('utf-8')
                    message_data = json.loads(message_value)
                    
                    logger.info(f"Received message from topic '{msg.topic()}' partition {msg.partition()} offset {msg.offset()}")
                    
                    # Process the message
                    message_handler(message_data)
                    
                    # Commit the offset after successful processing
                    self.consumer.commit(msg)
                    
                    msg_count += 1
                    if max_messages and msg_count >= max_messages:
                        logger.info(f"Processed {msg_count} messages, stopping consumer")
                        break
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON message: {e}")
                    # Commit the problematic message to avoid getting stuck
                    self.consumer.commit(msg)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Don't commit the offset if processing failed to allow retry
                    # But we might want to implement dead letter queue logic here
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.close()

    def close(self):
        """Close the consumer and clean up resources."""
        self.running = False
        self.consumer.close()
        logger.info("Kafka consumer closed")


# Example message handler function
def example_message_handler(message_data: Dict[str, Any]):
    """Example handler for processing consumed messages."""
    logger.info(f"Processing message: {message_data}")
    # Add your custom processing logic here
    # For example, update database, trigger business logic, etc.


# Async wrapper for consuming messages
async def async_consume_messages(consumer: KafkaConsumer, message_handler: Callable[[Dict[str, Any]], None], max_messages: int = None):
    """Async wrapper for consuming messages."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, consumer.consume_messages, message_handler, max_messages)