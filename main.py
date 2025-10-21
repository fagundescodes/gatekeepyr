import asyncio
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
import httpx
import logging
from itertools import cycle
from contextlib import asynccontextmanager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(health_check_loop())
    yield


async def health_check_loop():
    while True:
        await check_health()
        await asyncio.sleep(5)


app = FastAPI(lifespan=lifespan)

URLS = [
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003",
]

backend_metrics = {
    "http://127.0.0.1:8001": 0,
    "http://127.0.0.1:8002": 0,
    "http://127.0.0.1:8003": 0,
}

backend_urls = cycle(URLS)
working_backends = URLS.copy()


@app.get("/")
async def root():
    return {"message": "Hello from gatekeepyr"}


@app.get("/health")
async def health():
    return {"status": "Ok"}


@app.get("/proxy/{path:path}")
async def proxy(path: str):
    backend = next(backend_urls)
    backend_metrics[backend] += 1
    url = f"{backend}/{path}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Backend service unavailable: {e}")
        raise HTTPException(503, "Service is not responding")


@app.get("/metrics")
async def metrics():
    return {
        "backends": backend_metrics,
        "total_requests": sum(backend_metrics.values()),
    }


async def check_health():
    global working_backends, backend_urls
    new_working_backends = []

    for backend in URLS:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{backend}/health")
                if response.status_code == 200:
                    new_working_backends.append(backend)
        except:
            logger.warning(f"Backend {backend} is down")
    working_backends = new_working_backends
    backend_urls = cycle(working_backends)
