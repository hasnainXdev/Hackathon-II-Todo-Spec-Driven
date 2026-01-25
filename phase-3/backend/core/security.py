from datetime import datetime, timedelta
from typing import Optional
import httpx
from jose import jwt, ExpiredSignatureError
from jose.exceptions import JWTError
from fastapi import HTTPException, status, Request
from core.config import settings
import time


class JWTHandler:
    def __init__(self):
        # Use BETTER_AUTH_SECRET to match what the frontend uses for token generation
        self.secret_key = settings.BETTER_AUTH_SECRET or settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        # Handle case where BETTER_AUTH_URL is not set
        if settings.BETTER_AUTH_URL:
            self.jwks_url = f"{settings.BETTER_AUTH_URL}/api/auth/jwks"
            self.issuer = settings.BETTER_AUTH_URL
            self.audience = settings.BETTER_AUTH_URL
        else:
            # Default values if BETTER_AUTH_URL is not set
            self.jwks_url = None
            self.issuer = None
            self.audience = None
        self._jwks_client = None
        self._jwks_last_fetched = 0
        self._jwks_cache_duration = 300  # Cache JWKS for 5 minutes

    async def get_jwks_client(self):
        current_time = time.time()

        # Refresh JWKS if cache is expired or empty
        if (
            self._jwks_client is None
            or (current_time - self._jwks_last_fetched) > self._jwks_cache_duration
        ):

            if not self.jwks_url:
                # If BETTER_AUTH_URL is not configured, return None to use local JWT
                return None

            # Fetch JWKS from Better Auth
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(self.jwks_url)
                    response.raise_for_status()  # Raise exception for bad status codes
                    jwks = response.json()

                    # Store the JWKS and update timestamp
                    self._jwks_client = jwks
                    self._jwks_last_fetched = current_time
                except httpx.RequestError as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to fetch JWKS: {str(e)}",
                    )
                except httpx.HTTPStatusError as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"JWKS endpoint returned error: {str(e)}",
                    )

        return self._jwks_client

    async def verify_token(self, token: str) -> dict:
        """
        Verify a JWT token - simplified approach
        """
        from core.logging_config import logger

        logger.info(f"Verifying token: {token[:20]}...")

        try:
            # The frontend encodes the secret using TextEncoder, so we need to handle it properly
            # For HS256, ensure we're using the secret in the same format
            secret_bytes = (
                self.secret_key.encode("utf-8")
                if isinstance(self.secret_key, str)
                else self.secret_key
            )

            payload = jwt.decode(token, secret_bytes, algorithms=[self.algorithm])
            return payload
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {e}",
            )


# Create a global instance
jwt_handler = JWTHandler()


async def get_current_user(request: Request) -> dict:
    """
    Dependency to get the current user from the JWT token
    """
    from core.logging_config import logger

    authorization = request.headers.get("Authorization")

    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("No valid Authorization header found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    token = authorization.replace("Bearer ", "")

    payload = await jwt_handler.verify_token(token)

    # Extract user info from the payload
    user_info = {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "name": payload.get("name"),
    }

    return user_info


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a local JWT token for development/testing purposes
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    # Use the same secret as token verification to ensure consistency
    secret_to_use = settings.BETTER_AUTH_SECRET or settings.SECRET_KEY
    encoded_jwt = jwt.encode(
        to_encode, secret_to_use, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
