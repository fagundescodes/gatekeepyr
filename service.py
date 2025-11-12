import asyncio
import os
import random
from datetime import datetime

from fastapi import FastAPI

app = FastAPI()

SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown")


@app.get("/")
async def root():
    delay = random.uniform(0.1, 0.5)
    await asyncio.sleep(delay)
    return {
        "service": SERVICE_NAME,
        "message": "Request processed with success",
        "timestamp": datetime.now().isoformat(),
        "delay": delay,
    }


@app.get("/health")
async def health():
    return {"status": "Ok"}
