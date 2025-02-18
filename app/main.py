from fastapi import FastAPI
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager
from app.routes.routes import router
from app.routes.auth import router as auth_router 
from app.elastic_utils import create_index
from app.config import REDIS_URL
from app.middleware.idempotency import IdempotencyMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Elasticsearch index...")
    create_index()
    print("Elasticsearch index created!")
    
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    
    yield

app = FastAPI(title="FastAPI + Elasticsearch", version="1.0.0", lifespan=lifespan)

# Add middlewares globally
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include authentication routes for OAuth2
app.include_router(auth_router)

# Include routes
app.include_router(router)
