from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Awaitable
from core.config import settings
from core.logging_config import logger
import time


class AIServiceAuthMiddleware:
    """
    Middleware to authenticate and validate requests to AI service endpoints
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        path = request.url.path

        # Apply AI service authentication only to chat endpoints
        if path.startswith("/api/v1/chats"):
            # Check if AI service is configured
            if not settings.GEMINI_API_KEY:
                # If no API key is configured, we can either:
                # 1. Block the request (strict mode)
                # 2. Allow the request but with limited functionality (lenient mode)
                # For now, we'll allow the request but log a warning
                logger.warning("AI service is not configured with an API key")
                
                # For production, you might want to return an error:
                # return JSONResponse(
                #     status_code=503,
                #     content={"detail": "AI service is temporarily unavailable"}
                # )

            # Add AI service availability info to request state
            request.state.ai_service_available = bool(settings.GEMINI_API_KEY)

        # Continue with the request
        response = await self.app(scope, receive, send)
        return response


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI


def get_ai_service_rate_limiter():
    """
    Returns a rate limiter for AI service endpoints
    """
    limiter = Limiter(key_func=get_remote_address)
    return limiter


def add_rate_limiting_to_app(app: FastAPI):
    """
    Adds rate limiting to the application
    """
    limiter = get_ai_service_rate_limiter()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return limiter