from confluent_kafka import Consumer, KafkaException
import json
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "notification-group"):
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 1000,
        }
        self.consumer = Consumer(self.consumer_config)
        
        # In a real implementation, you would configure email/smtp settings here
        # For this example, we'll just log notifications
        self.email_enabled = False  # Set to True to enable actual email sending

    def subscribe_to_reminder_topic(self):
        """Subscribe to the reminders topic."""
        self.consumer.subscribe(['reminders'])
        logger.info("Notification service subscribed to 'reminders' topic")

    def process_reminder_event(self, message_data: dict):
        """Process a reminder event and send notification."""
        try:
            task_id = message_data.get('payload', {}).get('task_id')
            title = message_data.get('payload', {}).get('title')
            due_date = message_data.get('payload', {}).get('due_date')
            user_id = message_data.get('payload', {}).get('user_id')
            
            logger.info(f"Processing reminder for task {task_id}: {title}")
            
            # In a real implementation, you would look up user's contact info
            # and send an actual notification (email, SMS, push notification)
            
            # For this example, we'll just log the notification
            notification_msg = f"Reminder: Task '{title}' is due {due_date}. Task ID: {task_id}"
            logger.info(f"Sending notification to user {user_id}: {notification_msg}")
            
            # If email was enabled, you would send an actual email here
            if self.email_enabled:
                self.send_email_notification(user_id, title, due_date, task_id)
            
            return True
        except Exception as e:
            logger.error(f"Error processing reminder event: {e}")
            return False

    def send_email_notification(self, user_id: str, title: str, due_date: str, task_id: str):
        """Send an email notification (placeholder implementation)."""
        # This is a placeholder - in a real implementation you would:
        # 1. Look up user's email address from the database
        # 2. Configure SMTP settings
        # 3. Send the actual email
        logger.info(f"Email notification would be sent to user {user_id} about task {title}")

    def start_listening(self):
        """Start listening for reminder events."""
        logger.info("Notification service starting to listen for events...")
        
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
                    
                    # Process the reminder event
                    self.process_reminder_event(message_data)
                    
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
            logger.info("Notification service interrupted by user")
        finally:
            self.consumer.close()


# For testing purposes
if __name__ == "__main__":
    service = NotificationService()
    service.subscribe_to_reminder_topic()
    service.start_listening()