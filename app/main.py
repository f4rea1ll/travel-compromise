from fastapi import FastAPI

app = FastAPI(title="Travel Compromise")

@app.get("/health")
def health_check():
    return {"status": "ok"}