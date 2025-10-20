from fastapi import FastAPI
from fastapi.exceptions import HTTPException
import httpx
import logging
from itertools import cycle


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="gatekeepyr")


URLS = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003",
]

backend_urls = cycle(URLS)


@app.get("/")
async def root():
    return {"message": "Hello from gatekeepyr"}


@app.get("/health")
async def health():
    return {"status": "Ok"}


@app.get("/proxy/{path:path}")
async def proxy(path: str):
    backend = next(backend_urls)
    url = f"{backend}/{path}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Backend service unavailable: {e}")
        raise HTTPException(503, "Service is not responding")
