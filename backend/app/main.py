
from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    description="Multimodal Document Intelligence Platform",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


@app.get("/")
def home():
    return {
        "project": settings.APP_NAME,
        "tagline": "From documents to trusted knowledge.",
        "message": "Welcome to VERITAS API!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": settings.APP_NAME
    }
