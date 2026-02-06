import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import traceback
from enum import Enum


class AILogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AIServiceLogger:
    """
    Comprehensive logging service for AI operations
    """
    
    def __init__(self, name: str = "AI_Service", log_file: str = "ai_service.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent adding handlers multiple times
        if not self.logger.handlers:
            # Create formatters
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            
            # File handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def log_event(self, level: AILogLevel, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """
        Log an event with optional extra data
        """
        log_message = message
        if extra_data:
            log_message += f" | Extra data: {extra_data}"
        
        if level == AILogLevel.DEBUG:
            self.logger.debug(log_message)
        elif level == AILogLevel.INFO:
            self.logger.info(log_message)
        elif level == AILogLevel.WARNING:
            self.logger.warning(log_message)
        elif level == AILogLevel.ERROR:
            self.logger.error(log_message)
        elif level == AILogLevel.CRITICAL:
            self.logger.critical(log_message)
    
    def log_ai_request(self, user_id: str, request: str, conversation_id: Optional[str] = None):
        """
        Log an incoming AI request
        """
        extra_data = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.log_event(AILogLevel.INFO, f"AI request received: {request[:50]}...", extra_data)
    
    def log_ai_response(self, user_id: str, request: str, response: str, conversation_id: Optional[str] = None):
        """
        Log an AI response
        """
        extra_data = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "request_preview": request[:50] + "..." if len(request) > 50 else request,
            "response_length": len(response),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.log_event(AILogLevel.INFO, f"AI response generated", extra_data)
    
    def log_error(self, error: Exception, context: str = "", extra_data: Optional[Dict[str, Any]] = None):
        """
        Log an error with full traceback
        """
        error_msg = f"{context} | Error: {str(error)} | Traceback: {traceback.format_exc()}"
        self.log_event(AILogLevel.ERROR, error_msg, extra_data)
    
    def log_nlp_processing(self, original_text: str, parsed_result: Dict[str, Any], user_id: str):
        """
        Log NLP processing results
        """
        extra_data = {
            "user_id": user_id,
            "original_text_length": len(original_text),
            "parsed_result_keys": list(parsed_result.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.log_event(AILogLevel.DEBUG, f"NLP processing completed for text: {original_text[:30]}...", extra_data)
    
    def log_task_operation(self, operation: str, user_id: str, task_details: Dict[str, Any], success: bool):
        """
        Log task operations (create, update, delete, complete)
        """
        extra_data = {
            "user_id": user_id,
            "operation": operation,
            "task_id": task_details.get('id', 'unknown'),
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        status = "successful" if success else "failed"
        self.log_event(AILogLevel.INFO, f"Task {operation} operation {status}", extra_data)
    
    def log_suggestion_generation(self, user_id: str, suggestion_type: str, suggestions: list):
        """
        Log suggestion generation
        """
        extra_data = {
            "user_id": user_id,
            "suggestion_type": suggestion_type,
            "number_of_suggestions": len(suggestions),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.log_event(AILogLevel.INFO, f"Generated {len(suggestions)} {suggestion_type} suggestions", extra_data)


def ai_log_errors(logger: AIServiceLogger):
    """
    Decorator to automatically log errors in AI service functions
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log_error(
                    error=e,
                    context=f"Error in function {func.__name__}",
                    extra_data={
                        "function_args": str(args)[:200],  # Limit length
                        "function_kwargs": str(kwargs)[:200]  # Limit length
                    }
                )
                raise
        return wrapper
    return decorator


# Global logger instance
ai_logger = AIServiceLogger()


def get_ai_logger() -> AIServiceLogger:
    """
    Get the global AI service logger instance
    """
    return ai_logger