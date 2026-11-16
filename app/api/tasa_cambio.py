from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from datetime import date

from app.database import get_db
from app.models.tasa_cambio import TasaCambio
from app.schemas.tasa_cambio import TasaCambioResponse
from app.security import verify_api_token
from app.services.tasa_cambio_scraper import sync_tasa_cambio_bcv, TasaCambioScraper

router = APIRouter(prefix="/tasa-cambio", tags=["Tasa de Cambio"], dependencies=[Depends(verify_api_token)])


@router.get(
    "/actual",
    response_model=TasaCambioResponse,
    summary="Obtener tasa USD/VES actual",
)
async def obtener_tasa_actual(
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene la tasa USD/VES más reciente registrada.
    """
    result = await db.execute(
        select(TasaCambio).order_by(TasaCambio.fecha.desc()).limit(1)
    )
    tasa = result.scalar_one_or_none()
    if not tasa:
        raise HTTPException(status_code=404, detail="No hay tasa de cambio registrada")
    return tasa


@router.post(
    "/sync",
    response_model=TasaCambioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sincronizar tasa USD/VES desde BCV",
)
async def sincronizar_tasa(
    db: AsyncSession = Depends(get_db),
):
    """
    Sincroniza la tasa USD/VES desde el BCV (scraping web oficial).
    """
    from app.services.tasa_cambio_scraper import TasaCambioScraper
    
    async with TasaCambioScraper() as scraper:
        tasa = await scraper.fetch_tasa_usd_ves()
        if not tasa:
            raise HTTPException(
                status_code=502,
                detail="No se pudo obtener la tasa del BCV. Verifique conectividad o intente más tarde."
            )
        
        # Guardar en BD (crea o actualiza)
        await scraper.save_tasa(tasa)
        
        # Obtener la tasa guardada
        result = await db.execute(
            select(TasaCambio).order_by(TasaCambio.fecha.desc()).limit(1)
        )
        tasa_obj = result.scalar_one_or_none()
        if not tasa_obj:
            raise HTTPException(status_code=500, detail="Error al obtener la tasa guardada")
        
        return tasa_obj


@router.get(
    "/historial",
    response_model=list[TasaCambioResponse],
    summary="Obtener historial de tasas",
)
async def obtener_historial(
    skip: int = 0,
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene el historial de tasas de cambio con paginación.
    """
    result = await db.execute(
        select(TasaCambio)
        .order_by(TasaCambio.fecha.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get(
    "/test-conectividad",
    summary="Probar conectividad con BCV",
)
async def test_conectividad():
    """
    Prueba la conectividad con el sitio web del BCV.
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get("https://www.bcv.org.ve", timeout=10.0)
            return {
                "status": "success",
                "status_code": response.status_code,
                "content_length": len(response.text),
                "message": "Conexión exitosa con BCV"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "No se pudo conectar con BCV"
        }


@router.get(
    "/debug-scraper",
    summary="Debug del scraper BCV",
)
async def debug_scraper():
    """
    Debug del scraper del BCV - muestra detalles de lo que encuentra.
    """
    from app.services.tasa_cambio_scraper import TasaCambioScraper
    
    async with TasaCambioScraper() as scraper:
        # Test tasas page
        tasas_result = await scraper._fetch_from_tasas_page()
        
        # Test homepage
        homepage_result = await scraper._fetch_from_homepage()
        
        return {
            "tasas_page_result": tasas_result,
            "homepage_result": homepage_result,
            "message": "Debug completado"
        }


@router.post(
    "/manual",
    response_model=TasaCambioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tasa manualmente (para testing)",
)
async def crear_tasa_manual(
    fecha: date,
    tasa_usd_ves: Decimal,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una tasa de cambio manualmente (útil para testing cuando el scraper falla).
    """
    from app.models.tasa_cambio import TasaCambio
    
    # Verificar si ya existe
    result = await db.execute(
        select(TasaCambio).where(TasaCambio.fecha == fecha)
    )
    existente = result.scalar_one_or_none()
    
    if existente:
        existente.tasa_usd_ves = tasa_usd_ves
        await db.commit()
        await db.refresh(existente)
        return existente
    
    nueva_tasa = TasaCambio(
        fecha=fecha,
        tasa_usd_ves=tasa_usd_ves,
        fuente="MANUAL"
    )
    db.add(nueva_tasa)
    await db.commit()
    await db.refresh(nueva_tasa)
    return nueva_tasa