from fastapi import FastAPI

from app.presentation.api import router

app = FastAPI(title="IoT Store API", version="1.0.0")
app.include_router(router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
