from typing import Optional

from fastapi import FastAPI, Request

import asyncio
import aioredis

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

REDIS_BASE_URL = "redis://:local_password@db:6379"

limiter = Limiter(key_func=get_remote_address, storage_uri=f"{REDIS_BASE_URL}/0")
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    return {"Hello": "World"}

@app.get("/inject-redis")
async def inject_redis(key: str, value: str):
    redis = aioredis.from_url(f"{REDIS_BASE_URL}/11")

    # await redis.set(key, value)
    # await redis.expire(key, 20)

    await redis.execute_command('set', key, value, 'ex', 99)
    
    value = await redis.get(key)
    return { key: value}

@app.get("/update-redis-value")
async def inject_redis(key: str, value: str):
    redis = aioredis.from_url(f"{REDIS_BASE_URL}/11")

    await redis.set(key, value)

    value = await redis.get(key)
    return { key: value}
