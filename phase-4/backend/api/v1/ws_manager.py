from typing import Dict, List
import json
from fastapi import WebSocket, WebSocketDisconnect
from core.logging_config import logger


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        
        # Initialize user's connection list if it doesn't exist
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            
        # Add the new connection to the user's list
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                
                # Clean up user entry if no more connections
                if len(self.active_connections[user_id]) == 0:
                    del self.active_connections[user_id]
                    
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            logger.warning(f"Failed to send message to disconnected WebSocket: {message}")
            # Remove the disconnected socket from the manager
            # Note: We can't remove it here without knowing the user_id

    async def broadcast_to_user(self, message: str, user_id: str):
        if user_id in self.active_connections:
            disconnected_websockets = []
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message)
                except WebSocketDisconnect:
                    logger.warning(f"WebSocket disconnected during broadcast to user {user_id}")
                    disconnected_websockets.append(websocket)
            
            # Remove disconnected websockets from the manager
            for websocket in disconnected_websockets:
                self.disconnect(websocket, user_id)

    async def broadcast_to_all(self, message: str):
        disconnected_websockets = []
        
        for user_id, websockets in self.active_connections.items():
            for websocket in websockets:
                try:
                    await websocket.send_text(message)
                except WebSocketDisconnect:
                    logger.warning(f"WebSocket disconnected during broadcast to user {user_id}")
                    disconnected_websockets.append((websocket, user_id))
        
        # Remove disconnected websockets from the manager
        for websocket, user_id in disconnected_websockets:
            self.disconnect(websocket, user_id)


manager = ConnectionManager()