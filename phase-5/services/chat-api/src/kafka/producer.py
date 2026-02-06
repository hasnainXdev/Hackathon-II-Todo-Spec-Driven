from confluent_kafka import Producer
import json
import logging
from typing import Dict, Any
import asyncio
import threading
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
            'enable.idempotence': True,  # Ensures message delivery exactly once
            'acks': 'all',
            'retries': 3,
            'batch.num.messages': 10000,
            'linger.ms': 5,
            'compression.type': 'snappy'
        }
        self.producer = Producer(self.producer_config)
        self.stats_lock = threading.Lock()
        self.delivery_reports = []

    def delivery_report(self, err, msg):
        """Called once for each message produced to indicate delivery result."""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')
            with self.stats_lock:
                self.delivery_reports.append({
                    'topic': msg.topic(),
                    'partition': msg.partition(),
                    'offset': msg.offset(),
                    'timestamp': datetime.now().isoformat()
                })

    def produce_event(self, topic: str, event_data: Dict[str, Any], key: str = None):
        """
        Produce an event to the specified Kafka topic.
        
        Args:
            topic: The Kafka topic to send the event to
            event_data: The event data to send
            key: Optional key for partitioning
        """
        try:
            # Convert event_data to JSON string
            event_json = json.dumps(event_data, default=str)
            
            # Produce the message
            self.producer.produce(
                topic=topic,
                value=event_json,
                key=key,
                callback=self.delivery_report
            )
            
            # Poll for delivery reports to handle callbacks
            self.producer.poll(0)
            
            logger.info(f"Event queued for delivery to topic '{topic}' with key '{key}'")
            
        except Exception as e:
            logger.error(f"Error producing event to topic '{topic}': {e}")
            raise

    def flush(self, timeout: float = 30.0):
        """
        Flush all outstanding messages to Kafka.
        
        Args:
            timeout: Maximum time to wait for flush to complete
            
        Returns:
            Number of messages remaining after flush
        """
        logger.info("Flushing outstanding messages...")
        remaining = self.producer.flush(timeout)
        logger.info(f"Flush completed. {remaining} messages remaining.")
        return remaining

    def get_delivery_stats(self):
        """Get statistics about message deliveries."""
        with self.stats_lock:
            stats = {
                'total_delivered': len(self.delivery_reports),
                'recent_deliveries': self.delivery_reports[-10:]  # Last 10 deliveries
            }
        return stats


# Global producer instance
_kafka_producer = None


def get_kafka_producer(bootstrap_servers: str = "localhost:9092") -> KafkaProducer:
    """Get or create a singleton Kafka producer instance."""
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = KafkaProducer(bootstrap_servers)
    return _kafka_producer


async def async_produce_event(topic: str, event_data: Dict[str, Any], key: str = None):
    """Async wrapper for producing events."""
    producer = get_kafka_producer()
    loop = asyncio.get_event_loop()
    
    # Run the synchronous produce operation in a thread pool
    await loop.run_in_executor(None, producer.produce_event, topic, event_data, key)