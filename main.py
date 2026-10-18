
import os
import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

redis_url = os.getenv("REDIS_URL")
if not redis_url:
    raise RuntimeError("REDIS_URL environment variable is required")

r = redis.Redis.from_url(
    redis_url,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

@app.get("/healthz")
def healthz():
    try:
        r.ping()
        return {"status": "ok", "redis": "up"}
    except redis.RedisError:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "redis": "down"}
        )

@app.post("/hit/{key}")
def hit(key: str):
    try:
        count = r.incr(f"counter:{key}")
        return {"key": key, "count": count}
    except redis.RedisError:
        raise HTTPException(
            status_code=503, detail="Redis unavailable"
        )

@app.get("/count/{key}")
def count(key: str):
    try:
        value = r.get(f"counter:{key}")
        return {"key": key, "count": int(value) if value else 0}
    except redis.RedisError:
        raise HTTPException(
            status_code=503, detail="Redis unavailable"
        )
