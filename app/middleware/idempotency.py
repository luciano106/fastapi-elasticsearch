import logging
import hashlib

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import redis_client

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            logger.info(f"Request to {request.url.path} WITHOUT Idempotency-Key")
            return await call_next(request)  # If there is no key, continue as normal

        # Generate a hash of the key + endpoint URL
        cache_key = f"idempotency:{hashlib.sha256((idempotency_key + request.url.path).encode()).hexdigest()}"

        # Check if the key already exists in Redis
        if await redis_client.exists(cache_key):
            logger.warning(f"Duplicate request detected for {request.url.path} with key {idempotency_key}")
            raise HTTPException(status_code=409, detail="Duplicate request detected")

        # Store the key in Redis for 10 minutes
        await redis_client.setex(cache_key, 600, "processed")
        logger.info(f"Request to {request.url.path} stored with Idempotency-Key: {idempotency_key}")

        return await call_next(request)
