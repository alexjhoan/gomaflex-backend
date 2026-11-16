import re
from datetime import date
from decimal import Decimal
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from app.config import get_settings
from app.database import get_db
from app.models.tasa_cambio import TasaCambio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)


class TasaCambioScraper:
    """Scraper para obtener la tasa USD/VES oficial del BCV."""

    BCV_URL = "https://www.bcv.org.ve"
    TASA_URL = "https://www.bcv.org.ve/tasas-informativas-sistema-bancario"

    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "es-VE,es;q=0.9,en;q=0.8",
            },
            follow_redirects=True,
            verify=False,  # Deshabilitar verificación SSL para BCV
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def fetch_tasa_usd_ves(self) -> Optional[Decimal]:
        """
        Obtiene la tasa USD/VES oficial del BCV.
        Retorna la tasa como Decimal o None si falla.
        """
        try:
            logger.info("Iniciando obtención de tasa USD/VES del BCV")
            tasa = await self._fetch_from_tasas_page()
            if tasa:
                return tasa

            tasa = await self._fetch_from_homepage()
            if tasa:
                return tasa

            logger.warning("No se pudo obtener la tasa USD/VES del BCV")
            return None

        except Exception as e:
            logger.error(f"Error al obtener tasa del BCV: {e}")
            return None

    async def _fetch_from_tasas_page(self) -> Optional[Decimal]:
        """Obtiene la tasa desde la página de tasas informativas del BCV."""
        try:
            logger.info(f"Intentando obtener tasa desde: {self.TASA_URL}")
            response = await self.client.get(self.TASA_URL)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response length: {len(response.text)}")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Buscar el div con id="dolar" que contiene la tasa del dólar
            dolar_div = soup.find('div', id='dolar')
            if dolar_div:
                logger.info("Encontrado div con id='dolar'")
                # Buscar el strong con class="strong-tb" que contiene la tasa
                strong_tag = dolar_div.find('strong', class_='strong-tb')
                if strong_tag:
                    text = strong_tag.get_text(strip=True)
                    logger.info(f"Texto encontrado en strong.strong-tb: {text}")
                    # El formato es "914,02180000" - reemplazar coma por punto
                    match = re.search(r'(\d{1,3}(?:[.,]\d{4}))', text.replace(',', '.'))
                    if match:
                        try:
                            tasa = Decimal(match.group(1).replace(',', '.'))
                            if 10 < tasa < 2000:  # Rango válido para tasa USD/VES
                                logger.info(f"Tasa USD/VES encontrada en página de tasas: {tasa}")
                                return tasa
                        except Exception as e:
                            logger.warning(f"Error parseando tasa: {e}")
                            pass

            # Fallback: buscar en toda la página por el patrón
            logger.info("No se encontró en estructura esperada, buscando en toda la página...")
            return await self._fetch_from_homepage()

        except Exception as e:
            logger.warning(f"Error al obtener tasa de página de tasas: {e}")
            return None

    async def _fetch_from_homepage(self) -> Optional[Decimal]:
        """Intenta obtener la tasa desde la página principal del BCV."""
        try:
            response = await self.client.get(self.BCV_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Buscar en toda la página por el patrón de tasa
            text = soup.get_text()

            patterns = [
                r'USD\s*[:=]?\s*(\d{1,3}[.,]\d{4})',
                r'D[OÓ]LAR\s*[:=]?\s*(\d{1,3}[.,]\d{4})',
                r'TASA\s*USD\s*[:=]?\s*(\d{1,3}[.,]\d{4})',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        tasa = Decimal(match.replace(',', '.'))
                        if 10 < tasa < 2000:
                            logger.info(f"Tasa USD/VES encontrada en homepage: {tasa}")
                            return tasa
                    except:
                        continue

            return None

        except Exception as e:
            logger.warning(f"Error al obtener tasa de homepage: {e}")
            return None

    async def save_tasa(self, tasa: Decimal, fecha: date = None) -> bool:
        """
        Guarda la tasa en la base de datos.
        Retorna True si se guardó, False si ya existía.
        """
        if fecha is None:
            fecha = date.today()

        async for db in get_db():
            try:
                result = await db.execute(
                    select(TasaCambio).where(TasaCambio.fecha == fecha)
                )
                existente = result.scalar_one_or_none()

                if existente:
                    if existente.tasa_usd_ves != Decimal(str(tasa)):
                        existente.tasa_usd_ves = Decimal(str(tasa))
                        await db.commit()
                        logger.info(f"Tasa USD/VES actualizada para {fecha}: {tasa}")
                    return False

                nueva_tasa = TasaCambio(
                    fecha=fecha,
                    tasa_usd_ves=Decimal(str(tasa)),
                    fuente="BCV"
                )
                db.add(nueva_tasa)
                await db.commit()
                logger.info(f"Nueva tasa USD/VES guardada para {fecha}: {tasa}")
                return True

            except Exception as e:
                logger.error(f"Error al guardar tasa: {e}")
                return False


async def sync_tasa_cambio_bcv() -> bool:
    """
    Función para sincronizar la tasa desde el BCV.
    Puede usarse como task programada (cron job).
    """
    async with TasaCambioScraper() as scraper:
        tasa = await scraper.fetch_tasa_usd_ves()
        if tasa:
            return await scraper.save_tasa(tasa)
        return False