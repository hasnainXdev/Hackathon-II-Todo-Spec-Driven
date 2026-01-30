import json
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from sqlmodel import Session, select
from .models.conversation import Conversation, Message
from .models.user import User
import logging


class ChatHistoryBackupManager:
    """
    Manager for backing up and restoring chat history
    """
    
    def __init__(self, backup_dir: str = "./backups", session: Session = None):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self, user_id: Optional[str] = None, backup_name: Optional[str] = None) -> str:
        """
        Create a backup of chat history
        """
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"chat_backup_{timestamp}"
        
        if user_id:
            backup_name += f"_user_{user_id}"
        
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        try:
            # Prepare data to backup
            backup_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "user_id": user_id,
                    "backup_type": "chat_history"
                },
                "conversations": [],
                "messages": []
            }
            
            # Query conversations and messages
            if user_id:
                # Backup for specific user
                conv_statement = select(Conversation).where(Conversation.user_id == user_id)
                conversations = self.session.exec(conv_statement).all()
            else:
                # Backup all conversations
                conv_statement = select(Conversation)
                conversations = self.session.exec(conv_statement).all()
            
            for conv in conversations:
                conv_data = {
                    "id": conv.id,
                    "user_id": conv.user_id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                backup_data["conversations"].append(conv_data)
                
                # Get messages for this conversation
                msg_statement = select(Message).where(Message.conversation_id == conv.id)
                messages = self.session.exec(msg_statement).all()
                
                for msg in messages:
                    msg_data = {
                        "id": msg.id,
                        "user_id": msg.user_id,
                        "conversation_id": msg.conversation_id,
                        "task_id": msg.task_id,
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at.isoformat()
                    }
                    backup_data["messages"].append(msg_data)
            
            # Write backup data to a temporary file
            temp_json_path = self.backup_dir / f"{backup_name}.json"
            with open(temp_json_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Create zip archive
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_json_path, arcname=f"{backup_name}.json")
            
            # Remove temporary JSON file
            temp_json_path.unlink()
            
            self.logger.info(f"Backup created successfully: {backup_path}")
            return str(backup_path)
        
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            raise e
    
    def restore_backup(self, backup_path: str, user_id: Optional[str] = None) -> bool:
        """
        Restore chat history from a backup
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Extract the backup file
            extract_dir = self.backup_dir / "temp_extract"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            # Find the JSON file in the extracted content
            json_files = list(extract_dir.glob("*.json"))
            if not json_files:
                raise ValueError("No JSON backup file found in the archive")
            
            json_file = json_files[0]
            
            # Load the backup data
            with open(json_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validate backup data
            if "conversations" not in backup_data or "messages" not in backup_data:
                raise ValueError("Invalid backup file format")
            
            # Restore conversations and messages
            restored_conv_count = 0
            restored_msg_count = 0
            
            for conv_data in backup_data["conversations"]:
                # If restoring for a specific user, check if this conversation belongs to that user
                if user_id and conv_data["user_id"] != user_id:
                    continue
                
                # Create conversation object
                conversation = Conversation(
                    id=conv_data["id"],
                    user_id=conv_data["user_id"],
                    title=conv_data["title"],
                    created_at=datetime.fromisoformat(conv_data["created_at"]),
                    updated_at=datetime.fromisoformat(conv_data["updated_at"])
                )
                
                # Add to session (without committing yet to avoid conflicts)
                try:
                    self.session.add(conversation)
                    self.session.flush()  # This assigns an ID if needed
                    restored_conv_count += 1
                except Exception as e:
                    # Skip if conversation already exists
                    self.logger.warning(f"Skipping existing conversation {conv_data['id']}: {str(e)}")
                    continue
            
            for msg_data in backup_data["messages"]:
                # If restoring for a specific user, check if this message belongs to that user
                if user_id and msg_data["user_id"] != user_id:
                    continue
                
                # Create message object
                message = Message(
                    id=msg_data["id"],
                    user_id=msg_data["user_id"],
                    conversation_id=msg_data["conversation_id"],
                    task_id=msg_data.get("task_id"),
                    role=msg_data["role"],
                    content=msg_data["content"],
                    created_at=datetime.fromisoformat(msg_data["created_at"])
                )
                
                # Add to session
                try:
                    self.session.add(message)
                    self.session.flush()  # This assigns an ID if needed
                    restored_msg_count += 1
                except Exception as e:
                    # Skip if message already exists
                    self.logger.warning(f"Skipping existing message {msg_data['id']}: {str(e)}")
                    continue
            
            # Commit the transaction
            self.session.commit()
            
            # Cleanup
            shutil.rmtree(extract_dir)
            
            self.logger.info(f"Backup restored successfully: {restored_conv_count} conversations, {restored_msg_count} messages")
            return True
        
        except Exception as e:
            self.logger.error(f"Error restoring backup: {str(e)}")
            # Rollback in case of error
            self.session.rollback()
            raise e
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        """
        backups = []
        
        for backup_file in self.backup_dir.glob("*.zip"):
            try:
                # Extract metadata from the backup file
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # Find the JSON file in the archive
                    json_files = [name for name in zipf.namelist() if name.endswith('.json')]
                    if json_files:
                        with zipf.open(json_files[0]) as json_file:
                            metadata = json.loads(json_file.read().decode('utf-8'))["metadata"]
                            
                            backups.append({
                                "filename": backup_file.name,
                                "size": backup_file.stat().st_size,
                                "created_at": metadata["created_at"],
                                "user_id": metadata.get("user_id"),
                                "backup_type": metadata.get("backup_type")
                            })
            except Exception as e:
                self.logger.warning(f"Could not read backup file {backup_file}: {str(e)}")
                # Add basic info even if we can't read metadata
                backups.append({
                    "filename": backup_file.name,
                    "size": backup_file.stat().st_size,
                    "created_at": None,
                    "user_id": None,
                    "backup_type": "unknown"
                })
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x["created_at"] or "0000-00-00T00:00:00", reverse=True)
        return backups
    
    def delete_backup(self, backup_filename: str) -> bool:
        """
        Delete a backup file
        """
        backup_path = self.backup_dir / backup_filename
        
        if backup_path.exists():
            backup_path.unlink()
            self.logger.info(f"Backup deleted: {backup_filename}")
            return True
        else:
            self.logger.warning(f"Backup file not found: {backup_filename}")
            return False
    
    def get_backup_info(self, backup_filename: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific backup
        """
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return None
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Find the JSON file in the archive
                json_files = [name for name in zipf.namelist() if name.endswith('.json')]
                if not json_files:
                    return None
                
                with zipf.open(json_files[0]) as json_file:
                    backup_data = json.loads(json_file.read().decode('utf-8'))
                    
                    return {
                        "filename": backup_filename,
                        "size": backup_path.stat().st_size,
                        "metadata": backup_data.get("metadata", {}),
                        "conversation_count": len(backup_data.get("conversations", [])),
                        "message_count": len(backup_data.get("messages", []))
                    }
        except Exception as e:
            self.logger.error(f"Error reading backup info: {str(e)}")
            return None


# Example usage:
# backup_manager = ChatHistoryBackupManager(session=session)
# backup_path = backup_manager.create_backup(user_id="user123")
# backups = backup_manager.list_backups()
# success = backup_manager.restore_backup(backup_path, user_id="user123")