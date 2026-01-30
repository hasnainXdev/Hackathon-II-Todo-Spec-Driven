from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user_id(request: Request) -> str:
    """
    Extract and verify user ID from the request
    This is a simplified implementation - in production, you'd integrate with your auth system
    """
    # In a real implementation, this would decode the JWT token using better-auth
    # and extract the user ID from it
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    
    try:
        # This is a placeholder - in reality, you'd use better-auth to validate the token
        # For now, we'll simulate decoding a JWT to extract user info
        # decoded_token = jwt.decode(token, options={"verify_signature": False})
        # user_id = decoded_token.get("userId")
        
        # Since we're building on the existing phase-2 foundation, 
        # we'll use the same authentication approach
        # For now, returning a placeholder - this will be implemented with better-auth
        user_id = "placeholder_user_id"  # This should come from your auth system
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error extracting user ID: {e}")
        raise HTTPException(status_code=401, detail="Authentication error")


def require_api_key():
    """
    Dependency to require a valid API key for AI service endpoints
    """
    async def api_key_dependency(request: Request):
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
        
        if not api_key:
            raise HTTPException(status_code=401, detail="API key is required")
        
        # In a real implementation, you'd validate the API key against a database
        # For now, we'll just check if it's present
        expected_api_key = "expected_api_key_value"  # This should come from env vars
        if api_key != expected_api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key_dependency