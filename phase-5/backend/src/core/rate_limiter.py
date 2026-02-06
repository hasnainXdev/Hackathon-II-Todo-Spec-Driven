import time
from typing import Dict, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import threading


class RateLimiter:
    """
    Rate limiter for AI service endpoints
    """
    
    def __init__(self):
        # Store request timestamps for each user
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()  # Thread-safe access
    
    def is_allowed(self, user_id: str, limit: int, window: int) -> bool:
        """
        Check if a request from user_id is allowed based on rate limits
        
        Args:
            user_id: The ID of the requesting user
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            user_requests = self.requests[user_id]
            
            # Remove requests that are outside the time window
            while user_requests and user_requests[0] < now - window:
                user_requests.popleft()
            
            # Check if the user has exceeded the limit
            if len(user_requests) >= limit:
                return False
            
            # Add the current request
            user_requests.append(now)
            return True


class AIServiceRateLimiter:
    """
    Specialized rate limiter for AI service endpoints with different tiers
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        
        # Different rate limits for different tiers of users
        self.limits = {
            "free": {"limit": 10, "window": 60},  # 10 requests per minute
            "basic": {"limit": 50, "window": 60},  # 50 requests per minute
            "premium": {"limit": 200, "window": 60},  # 200 requests per minute
            "enterprise": {"limit": 1000, "window": 60}  # 1000 requests per minute
        }
        
        # Default to free tier if user tier not found
        self.default_tier = "free"
    
    def check_rate_limit(self, user_id: str, user_tier: Optional[str] = None) -> bool:
        """
        Check if a request from user is within rate limits
        
        Args:
            user_id: The ID of the requesting user
            user_tier: The tier of the user (free, basic, premium, enterprise)
            
        Returns:
            True if request is allowed, raises HTTPException if not
        """
        if not user_tier:
            user_tier = self.default_tier
        
        # Get the limits for the user's tier
        tier_limits = self.limits.get(user_tier, self.limits[self.default_tier])
        
        # Check if the request is allowed
        if not self.rate_limiter.is_allowed(user_id, tier_limits["limit"], tier_limits["window"]):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"You have exceeded your rate limit of {tier_limits['limit']} requests "
                              f"per {tier_limits['window']} seconds. Please try again later."
                }
            )
        
        return True
    
    def get_reset_time(self, user_id: str, user_tier: Optional[str] = None) -> int:
        """
        Get the time when the rate limit will reset for the user
        """
        if not user_tier:
            user_tier = self.default_tier
        
        tier_limits = self.limits.get(user_tier, self.limits[self.default_tier])
        
        with self.rate_limiter.lock:
            user_requests = self.rate_limiter.requests[user_id]
            
            if not user_requests:
                # No requests recorded, limit resets immediately
                return int(time.time())
            
            # The reset time is the oldest request time plus the window
            oldest_request = user_requests[0] if user_requests else time.time()
            reset_time = int(oldest_request + tier_limits["window"])
            
            return reset_time
    
    def get_remaining_requests(self, user_id: str, user_tier: Optional[str] = None) -> int:
        """
        Get the number of remaining requests for the user in the current window
        """
        if not user_tier:
            user_tier = self.default_tier
        
        tier_limits = self.limits.get(user_tier, self.limits[self.default_tier])
        
        with self.rate_limiter.lock:
            user_requests = self.rate_limiter.requests[user_id]
            
            # Remove expired requests
            now = time.time()
            while user_requests and user_requests[0] < now - tier_limits["window"]:
                user_requests.popleft()
            
            return tier_limits["limit"] - len(user_requests)


# Global rate limiter instance
ai_rate_limiter = AIServiceRateLimiter()


def get_ai_rate_limiter() -> AIServiceRateLimiter:
    """
    Get the global AI service rate limiter instance
    """
    return ai_rate_limiter


# Example middleware function that could be used with FastAPI
async def rate_limit_middleware(user_id: str, user_tier: Optional[str] = None):
    """
    Middleware function to check rate limits before processing requests
    """
    rate_limiter = get_ai_rate_limiter()
    rate_limiter.check_rate_limit(user_id, user_tier)
    
    # Add rate limit headers to response
    remaining = rate_limiter.get_remaining_requests(user_id, user_tier)
    reset_time = rate_limiter.get_reset_time(user_id, user_tier)
    
    return {
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_time)
    }