import os
import random

from fastapi import FastAPI, HTTPException

app = FastAPI()

SERVICE_NAME = os.getenv("SERVICE_NAME", "breaker")
FAIL_RATE = float(os.getenv("FAIL_RATE", "0.8"))


@app.get("/")
async def root():
    if random.random() < FAIL_RATE:
        raise HTTPException(status_code=500, detail="Simulated failure")

    return {
        "service": SERVICE_NAME,
        "message": "Request processed",
    }


@app.get("/health")
async def health():
    return {"status": "Ok"}
