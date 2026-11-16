from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from app.models.contacto import AsuntoContacto
from datetime import datetime


class ContactoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=50)
    asunto: AsuntoContacto
    mensaje: str = Field(..., min_length=10, max_length=3000)


class ContactoCreate(ContactoBase):
    pass


class ContactoResponse(ContactoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True