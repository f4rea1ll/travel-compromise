from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import session

app = FastAPI(title="Travel Compromise")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}