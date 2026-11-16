from app.api.sugerencias import router as sugerencias_router
from app.api.contacto import router as contacto_router
from app.api.tasa_cambio import router as tasa_cambio_router

__all__ = ["sugerencias_router", "contacto_router", "tasa_cambio_router"]