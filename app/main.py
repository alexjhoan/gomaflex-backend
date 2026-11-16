import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.database import init_db
from app.api import sugerencias_router, contacto_router, tasa_cambio_router
from app.services.tasa_cambio_scraper import sync_tasa_cambio_bcv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Scheduler para tareas programadas
scheduler = AsyncIOScheduler()


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    
    # Iniciar scheduler para tareas programadas
    # Ejecutar a las 2 PM (14:00) de lunes a viernes (hora de Venezuela UTC-4)
    scheduler.add_job(
        sync_tasa_cambio_bcv,
        trigger=CronTrigger(hour=14, minute=0, day_of_week='mon-fri', timezone='America/Caracas'),
        id='sync_tasa_cambio_bcv',
        name='Sincronizar tasa USD/VES desde BCV',
        replace_existing=True
    )
    scheduler.start()
    logging.info("Scheduler iniciado - Sincronización de tasa USD/VES programada para las 2:00 PM (lunes-viernes)")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logging.info("Scheduler detenido")


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
app.include_router(tasa_cambio_router)


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
            "tasa-cambio": "/tasa-cambio",
        },
    }