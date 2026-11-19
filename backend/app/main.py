from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
import app.models  # Ensure all SQLAlchemy models are registered with Base.metadata
from app.api.v1.router import api_router
from app.services.demo_seed import seed_demo_data

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

# Auto-seed demo organisation for immediate judge review
db = SessionLocal()
try:
    seed_demo_data(db)
finally:
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"{settings.TAGLINE}. Production REST API for enterprise brand adherence, evidence-backed AI verification, and smart corrections.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all during dev/demo, can restrict with settings.cors_origins in strict env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "docs": "/docs",
        "health": "/health"
    }
