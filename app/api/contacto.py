from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.contacto import Contacto
from app.schemas.contacto import ContactoCreate, ContactoResponse
from app.security import verify_api_token

router = APIRouter(prefix="/contacto", tags=["Contacto"], dependencies=[Depends(verify_api_token)])


@router.post(
    "/",
    response_model=ContactoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo mensaje de contacto",
)
async def crear_contacto(
    contacto: ContactoCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea un nuevo mensaje de contacto en la base de datos.
    """
    nuevo_contacto = Contacto(
        nombre=contacto.nombre,
        email=contacto.email,
        telefono=contacto.telefono,
        asunto=contacto.asunto,
        mensaje=contacto.mensaje,
    )
    db.add(nuevo_contacto)
    await db.commit()
    await db.refresh(nuevo_contacto)
    return nuevo_contacto


@router.get(
    "/",
    response_model=list[ContactoResponse],
    summary="Listar todos los contactos",
)
async def listar_contactos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Lista todos los mensajes de contacto con paginación.
    """
    result = await db.execute(
        select(Contacto).offset(skip).limit(limit).order_by(Contacto.created_at.desc())
    )
    return result.scalars().all()


@router.get(
    "/{contacto_id}",
    response_model=ContactoResponse,
    summary="Obtener contacto por ID",
)
async def obtener_contacto(
    contacto_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene un mensaje de contacto por su ID.
    """
    result = await db.execute(select(Contacto).where(Contacto.id == contacto_id))
    contacto = result.scalar_one_or_none()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    return contacto