from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class AsuntoContacto(str, enum.Enum):
    COTIZACION = "cotizacion"
    REPUESTO = "repuesto"
    TECNICO = "tecnico"
    DISTRIBUIDOR = "distribuidor"
    QUEJA = "queja"
    OTRO = "otro"


class Contacto(Base):
    __tablename__ = "contactos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    telefono = Column(String(50), nullable=True)
    asunto = Column(SQLEnum(AsuntoContacto), nullable=False)
    mensaje = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Contacto(id={self.id}, nombre={self.nombre}, email={self.email})>"