from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from app.models.sugerencia import TipoSugerencia
from datetime import datetime


class SugerenciaBase(BaseModel):
    tipo: TipoSugerencia = TipoSugerencia.OTRA
    mensaje: str = Field(..., min_length=10, max_length=2000)
    contacto: Optional[str] = Field(None, max_length=255)


class SugerenciaCreate(SugerenciaBase):
    pass


class SugerenciaResponse(SugerenciaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True