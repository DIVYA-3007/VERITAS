
from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.endpoints.documents import router as documents_router

from app.api.v1.endpoints.search import router as search_router
from app.api.v1.endpoints.qa import router as qa_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Multimodal Document Intelligence Platform",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


# Register API routers
app.include_router(
    documents_router,
    prefix=settings.API_V1_PREFIX,
)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(search_router, prefix=settings.API_V1_PREFIX)


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

app.include_router(qa_router, prefix=settings.API_V1_PREFIX)

