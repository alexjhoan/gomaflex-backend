from sqlalchemy import Column, Integer, Numeric, Date, DateTime, String, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class TasaCambio(Base):
    __tablename__ = "tasas_cambio"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, unique=True, index=True)
    tasa_usd_ves = Column(Numeric(precision=10, scale=4), nullable=False)
    fuente = Column(String(100), nullable=True, default="BCV")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('fecha', name='uq_tasa_cambio_fecha'),
    )

    def __repr__(self):
        return f"<TasaCambio(fecha={self.fecha}, tasa_usd_ves={self.tasa_usd_ves})>"