from fastapi import FastAPI
import httpx

app = FastAPI(title="gatekeepyr")


@app.get("/")
async def root():
    return {"message": "Hello from gatekeepyr"}


@app.get("/health")
async def health():
    return {"status": "Ok"}


@app.get("/proxy")
async def proxy():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://127.0.0.1:8001/")
        return r.json()
