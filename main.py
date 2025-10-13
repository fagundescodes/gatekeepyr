from fastapi import FastAPI

app = FastAPI(title="gatekeepyr")


@app.get("/")
async def root():
    return {"message": "Hello from gatekeepyr"}


@app.get("/health")
async def health():
    return {"status": "Ok"}
