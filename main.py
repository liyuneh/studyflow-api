
from fastapi import FastAPI

app = FastAPI(
    title="StudyFlow API",
    description="A study task management API and Health Monitor",
    version="0.1.0",
)


@app.get("/")
def home():
    return {"message": "Welcome to StudyFlow API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
