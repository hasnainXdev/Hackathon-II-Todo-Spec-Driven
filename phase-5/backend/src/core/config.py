import os
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from ..services.ai_service import AIService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIServiceConfig:
    """
    Configuration class for AI service
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
        
        # Validate required configuration
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY environment variable is not set")
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def get_ai_service(self) -> AIService:
        """
        Create and return an instance of AIService with current configuration
        """
        return AIService()


def setup_error_handling(app: FastAPI):
    """
    Set up global error handling for the application
    """
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception occurred: {exc}", exc_info=True)
        return {"detail": "An unexpected error occurred", "error_type": type(exc).__name__}


def configure_cors(app: FastAPI):
    """
    Configure CORS middleware for the application
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_app_lifespan(app: FastAPI):
    """
    Set up application lifespan events
    """
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        logger.info("Starting up AI Chatbot application...")
        
        # Initialize AI service
        ai_config = AIServiceConfig()
        app.state.ai_service = ai_config.get_ai_service()
        
        yield
        
        # Shutdown
        logger.info("Shutting down AI Chatbot application...")
    
    app.lifespan = lifespan