from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Union
import logging


class DataEncryptionService:
    """
    Service for encrypting and decrypting sensitive data at rest
    """
    
    def __init__(self, encryption_key: bytes = None):
        if encryption_key:
            self.key = encryption_key
        else:
            # In production, get the key from environment variables or a secure key management system
            key_env = os.environ.get("DATA_ENCRYPTION_KEY")
            if key_env:
                self.key = base64.urlsafe_b64decode(key_env.encode())
            else:
                # Generate a new key if none is provided (for development only)
                logging.warning("No encryption key provided. Generating a new key for development.")
                self.key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.key)
    
    def encrypt_data(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt sensitive data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = self.cipher_suite.encrypt(data)
        return encrypted_data
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """
        Decrypt sensitive data
        """
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
    
    def encrypt_task_content(self, task_title: str, task_description: str = "") -> dict:
        """
        Encrypt task content before storing in the database
        """
        encrypted_title = self.encrypt_data(task_title)
        encrypted_description = self.encrypt_data(task_description) if task_description else b""
        
        return {
            "encrypted_title": base64.b64encode(encrypted_title).decode('utf-8'),
            "encrypted_description": base64.b64encode(encrypted_description).decode('utf-8') if encrypted_description else "",
        }
    
    def decrypt_task_content(self, encrypted_title: str, encrypted_description: str = "") -> dict:
        """
        Decrypt task content after retrieving from the database
        """
        try:
            decrypted_title = self.decrypt_data(base64.b64decode(encrypted_title.encode('utf-8')))
            decrypted_description = ""
            if encrypted_description:
                decrypted_description = self.decrypt_data(base64.b64decode(encrypted_description.encode('utf-8')))
            
            return {
                "title": decrypted_title,
                "description": decrypted_description
            }
        except Exception as e:
            logging.error(f"Failed to decrypt task content: {str(e)}")
            raise
    
    def encrypt_message_content(self, message_content: str) -> str:
        """
        Encrypt message content before storing in the database
        """
        encrypted_content = self.encrypt_data(message_content)
        return base64.b64encode(encrypted_content).decode('utf-8')
    
    def decrypt_message_content(self, encrypted_content: str) -> str:
        """
        Decrypt message content after retrieving from the database
        """
        try:
            decrypted_content = self.decrypt_data(base64.b64decode(encrypted_content.encode('utf-8')))
            return decrypted_content
        except Exception as e:
            logging.error(f"Failed to decrypt message content: {str(e)}")
            raise
    
    def rotate_encryption_key(self, new_key: bytes = None) -> bytes:
        """
        Rotate the encryption key (for security best practices)
        """
        old_cipher_suite = self.cipher_suite
        
        if new_key:
            self.key = new_key
        else:
            # Generate a new key
            self.key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.key)
        
        # In a real implementation, you would need to re-encrypt all data with the new key
        # This is a simplified version that just returns the new key
        return self.key


# Global encryption service instance
encryption_service = DataEncryptionService()


def get_encryption_service() -> DataEncryptionService:
    """
    Get the global encryption service instance
    """
    return encryption_service


# Example usage:
# encryption_service = get_encryption_service()
# encrypted_data = encryption_service.encrypt_data("sensitive information")
# decrypted_data = encryption_service.decrypt_data(encrypted_data)