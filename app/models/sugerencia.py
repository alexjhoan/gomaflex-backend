from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class TipoSugerencia(str, enum.Enum):
    REPUESTO = "repuesto"
    WEB = "web"
    ATENCION = "atencion"
    OTRA = "otra"


class Sugerencia(Base):
    __tablename__ = "sugerencias"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(SQLEnum(TipoSugerencia), nullable=False, default=TipoSugerencia.OTRA)
    mensaje = Column(Text, nullable=False)
    contacto = Column(String(255), nullable=True)  # WhatsApp o email
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Sugerencia(id={self.id}, tipo={self.tipo.value})>"