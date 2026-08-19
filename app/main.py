from fastapi import FastAPI
from app.routers import session

app = FastAPI(title="Travel Compromise")

app.include_router(session.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}