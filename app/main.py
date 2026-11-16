from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db
from app.api import sugerencias_router, contacto_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (si hay cleanup necesario)


app = FastAPI(
    title=settings.APP_NAME,
    description="API backend para GOMAFLEX - Sugerencias y Contacto",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(sugerencias_router)
app.include_router(contacto_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "GOMAFLEX Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "sugerencias": "/sugerencias",
            "contacto": "/contacto",
        },
    }