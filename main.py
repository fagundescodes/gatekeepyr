import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from enum import Enum
from itertools import cycle

import httpx
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URLS = os.getenv(
    "BACKEND_URLS", "http://127.0.0.1:8001,http://127.0.0.1:8002,http://127.0.0.1:8003"
).split(",")
FAILURE_THRESHOLD = int(os.getenv("FAILURE_THRESHOLD", "3"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "5"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(health_check_loop())
    yield


async def health_check_loop():
    while True:
        await check_health()
        await asyncio.sleep(HEALTH_CHECK_INTERVAL)


app = FastAPI(
    title="Gatekeepyr",
    description="API Gateway with load balancing, circuit breaker and health checks",
    version="0.1.0",
    lifespan=lifespan,
)


class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


URLS = BACKEND_URLS

circuit_breakers = {
    url: {
        "state": State.CLOSED,
        "failures": 0,
        "failure_time": None,
    }
    for url in URLS
}

backend_metrics = {url: 0 for url in URLS}

backend_urls = cycle(URLS)
working_backends = URLS.copy()


@app.get("/")
async def root():
    return {"message": "Hello from gatekeepyr"}


@app.get("/health")
async def health():
    """Check health status"""
    return {"status": "Ok"}


@app.get("/proxy/{path:path}")
async def proxy(path: str):
    """
    Distributes requests across multiple backends using round-robin
    Circuit breaker protect against failures
    """
    backend = next(backend_urls)
    backend_metrics[backend] += 1
    url = f"{backend}/{path}"
    circuit = circuit_breakers[backend]

    if circuit["state"] == State.OPEN:

        if (
            circuit["failure_time"]
            and (time.time() - circuit["failure_time"]) >= TIMEOUT_SECONDS
        ):
            circuit["state"] = State.HALF_OPEN
            logger.warning(f"Backend {backend} is now HALF_OPEN")
        else:
            raise HTTPException(503, f"Circuit breaker OPEN for {backend}")

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url)

            response.raise_for_status()
            circuit["failures"] = 0
            if circuit["state"] == State.HALF_OPEN:
                circuit["state"] = State.CLOSED
                logger.info(f"Circuit {backend} is now CLOSED")
            return response.json()

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        circuit["failures"] += 1
        circuit["failure_time"] = time.time()

        if circuit["failures"] >= FAILURE_THRESHOLD:
            circuit["state"] = State.OPEN
            logger.warning(
                f"Circuit {backend} is now OPEN (failures: {circuit['failures']})"
            )
        logger.error(f"Backend {backend} service unavailable {e}:")
        raise HTTPException(503, "Service is not responding")


@app.get("/metrics")
async def metrics():
    """Show how many requests each backend has received"""
    return {
        "backends": backend_metrics,
        "total_requests": sum(backend_metrics.values()),
    }


async def check_health():
    global working_backends, backend_urls
    new_working_backends = []

    for backend in URLS:
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(f"{backend}/health")
                if response.status_code == 200:
                    new_working_backends.append(backend)
        except:
            logger.warning(f"Backend {backend} is down")
    if new_working_backends:
        working_backends = new_working_backends
        backend_urls = cycle(working_backends)
    else:
        logger.error("All backends are down!")
