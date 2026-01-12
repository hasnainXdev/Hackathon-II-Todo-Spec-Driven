import time
from collections import defaultdict, deque
from typing import Dict

from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


# Initialize the limiter with a default limit
limiter = Limiter(key_func=get_remote_address)

# Dictionary to store request timestamps per IP
request_times: Dict[str, deque] = defaultdict(deque)


def rate_limit(max_requests: int = 100, window_size: int = 60):
    """
    Rate limiting decorator
    :param max_requests: Maximum number of requests allowed
    :param window_size: Time window in seconds
    """
    def rate_limit_middleware(request: Request):
        client_ip = get_remote_address(request)
        current_time = time.time()
        
        # Clean old requests outside the window
        while (request_times[client_ip] and 
               request_times[client_ip][0] <= current_time - window_size):
            request_times[client_ip].popleft()
        
        # Check if limit exceeded
        if len(request_times[client_ip]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Add current request timestamp
        request_times[client_ip].append(current_time)
        
        return None
    
    return rate_limit_middleware