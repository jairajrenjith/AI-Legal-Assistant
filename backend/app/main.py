import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.database import Base, engine
from app.routes import cases, analysis, questionnaire, documents, settings as settings_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("legal-assistant")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Legal Assistant API...")
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    # Ensure upload and document directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("generated_documents", exist_ok=True)
    logger.info("Database tables created. Upload dirs ready.")
    yield
    logger.info("Shutting down Legal Assistant API.")


app = FastAPI(
    title="AI Legal Assistant API",
    description=(
        "AI-powered legal assistant for government agencies. "
        "Supports case classification, law identification, evidence management, "
        "document generation, and explainable AI decision support across 7 legal domains."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS — allow frontend dev server and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files — serve uploaded documents
if os.path.isdir(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Register all routers
app.include_router(cases.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(questionnaire.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(settings_router.router, prefix="/api/v1")


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "ai_enabled": bool(settings.OPENAI_API_KEY),
    }


@app.get("/")
def root():
    return {
        "message": "AI Legal Assistant API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
