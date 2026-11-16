from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.sugerencia import Sugerencia
from app.schemas.sugerencia import SugerenciaCreate, SugerenciaResponse
from app.security import verify_api_token

router = APIRouter(prefix="/sugerencias", tags=["Sugerencias"], dependencies=[Depends(verify_api_token)])


@router.post(
    "/",
    response_model=SugerenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva sugerencia",
)
async def crear_sugerencia(
    sugerencia: SugerenciaCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una nueva sugerencia en la base de datos.
    """
    nueva_sugerencia = Sugerencia(
        tipo=sugerencia.tipo,
        mensaje=sugerencia.mensaje,
        contacto=sugerencia.contacto,
    )
    db.add(nueva_sugerencia)
    await db.commit()
    await db.refresh(nueva_sugerencia)
    return nueva_sugerencia


@router.get(
    "/",
    response_model=list[SugerenciaResponse],
    summary="Listar todas las sugerencias",
)
async def listar_sugerencias(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista todas las sugerencias con paginación.
    """
    result = await db.execute(
        select(Sugerencia).offset(skip).limit(limit).order_by(Sugerencia.created_at.desc())
    )
    return result.scalars().all()


@router.get(
    "/{sugerencia_id}",
    response_model=SugerenciaResponse,
    summary="Obtener sugerencia por ID",
)
async def obtener_sugerencia(
    sugerencia_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene una sugerencia por su ID.
    """
    result = await db.execute(select(Sugerencia).where(Sugerencia.id == sugerencia_id))
    sugerencia = result.scalar_one_or_none()
    if not sugerencia:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada")
    return sugerencia