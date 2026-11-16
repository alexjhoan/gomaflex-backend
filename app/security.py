from fastapi import Header, HTTPException, status
from app.config import get_settings


async def verify_api_token(authorization: str = Header(None)) -> str:
    """
    Verifica que el token de autorización sea válido.
    Espera el formato: "Bearer <token>" o solo "<token>"
    """
    settings = get_settings()
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de autorización requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer el token (soporta "Bearer <token>" o solo "<token>")
    token = authorization
    if authorization.lower().startswith("bearer "):
        token = authorization[7:]  # Quita "Bearer "
    
    if token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token de autorización inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token