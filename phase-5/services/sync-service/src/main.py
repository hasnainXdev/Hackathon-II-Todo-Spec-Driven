import asyncio
import json
import logging
from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from confluent_kafka import Consumer, KafkaException
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global manager to handle WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected. Total connections for user: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected. Remaining connections for user: {len(self.active_connections.get(user_id, []))}")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except WebSocketDisconnect:
                    # Remove disconnected connections
                    self.disconnect(connection, user_id)

    async def broadcast_to_user(self, message: str, user_id: str):
        await self.send_personal_message(message, user_id)


manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Kafka consumer in background
    consumer_task = asyncio.create_task(start_kafka_consumer())
    yield
    # Shutdown
    consumer_task.cancel()


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Just keep the connection alive; messages will be pushed from Kafka events
            data = await websocket.receive_text()
            # Optionally handle client messages here
            logger.info(f"Received message from user {user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


async def start_kafka_consumer():
    """Start Kafka consumer to listen for events and broadcast to WebSocket clients."""
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'sync-service-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'auto.commit.interval.ms': 1000,
    }
    
    consumer = Consumer(consumer_config)
    consumer.subscribe(['task-events', 'reminders', 'task-updates'])
    
    logger.info("Sync service started listening for events...")
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            
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
                
                # Extract user ID from the event
                user_id = str(message_data.get('user_context', {}).get('user_id'))
                
                if user_id:
                    # Broadcast the event to the user's WebSocket connections
                    await manager.broadcast_to_user(json.dumps({
                        'type': 'event_update',
                        'event': message_data,
                        'timestamp': message_data.get('timestamp')
                    }), user_id)
                    
                    logger.info(f"Broadcast event to user {user_id}")
                
                # Commit the message
                consumer.commit(msg)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}")
                consumer.commit(msg)  # Commit to avoid getting stuck
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Don't commit on error to allow retry (in a real system you might want
                # more sophisticated error handling like dead letter queues)
    
    except asyncio.CancelledError:
        logger.info("Kafka consumer task was cancelled")
    except Exception as e:
        logger.error(f"Unexpected error in Kafka consumer: {e}")
    finally:
        consumer.close()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sync-service", "connections": len(manager.active_connections)}