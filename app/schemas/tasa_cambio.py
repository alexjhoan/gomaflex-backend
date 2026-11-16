from pydantic import BaseModel, Field
from typing import Optional
from app.models.tasa_cambio import TasaCambio
from datetime import date, datetime
from decimal import Decimal


class TasaCambioBase(BaseModel):
    fecha: date
    tasa_usd_ves: Decimal = Field(..., gt=0, description="Tasa USD/VES")
    fuente: Optional[str] = Field(None, max_length=100)


class TasaCambioCreate(TasaCambioBase):
    pass


class TasaCambioResponse(TasaCambioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True