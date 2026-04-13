import os

from fastapi import Depends, Header, HTTPException

from src.application.usuarios_service import UsuariosService
from src.domain.models import User
from src.infrastructure.cognito.auth_validator import CognitoTokenValidator
from src.infrastructure.cognito.cognito import CognitoRepository

# Leemos las variables de entorno una sola vez al cargar el módulo
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")

if not COGNITO_USER_POOL_ID:
    raise ValueError("COGNITO_USER_POOL_ID no está configurado")

# Singleton de infraestructura para caché de llaves
token_validator = CognitoTokenValidator(AWS_REGION, COGNITO_USER_POOL_ID)


# Inyección del Repositorio
def get_cognito_repo() -> CognitoRepository:
    return CognitoRepository(region=AWS_REGION, user_pool_id=COGNITO_USER_POOL_ID)


# Inyección del Servicio
def get_usuarios_service(
    repo: CognitoRepository = Depends(get_cognito_repo),
) -> UsuariosService:
    return UsuariosService(repo)


# Dependencias de Autenticación
async def get_current_user(authorization: str = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado o inválido")
    token = authorization.split(" ")[1]
    return await token_validator.verify_token(token)


def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.rol not in allowed_roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return current_user

    return role_checker
