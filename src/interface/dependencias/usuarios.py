import os

from fastapi import Depends, Header, HTTPException
from fastapi.security import SecurityScopes

from src.application.add_usuario import AddUsuarios
from src.application.delete_usuario import DeleteUsuarios
from src.application.get_usuario import GetUsuarios
from src.application.update_rol import UpdateUsuarios
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


def get_usuarios_service() -> GetUsuarios:
    return GetUsuarios(repository=get_cognito_repo())


def add_usuarios_service() -> AddUsuarios:
    return AddUsuarios(repository=get_cognito_repo())


def delete_usuarios_service() -> DeleteUsuarios:
    return DeleteUsuarios(repository=get_cognito_repo())


def update_rol_service() -> UpdateUsuarios:
    return UpdateUsuarios(repository=get_cognito_repo())


# Dependencias de Autenticación
async def get_current_user(
    security_scopes: SecurityScopes,
    authorization: str = Header(None),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")

    token = authorization.split(" ")[1]
    user = await token_validator.verify_token(token)

    if security_scopes.scopes:
        if user.rol not in security_scopes.scopes:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")

    return user


def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.rol == "sin_asignar":
            raise HTTPException(
                status_code=403,
                detail="Tu cuenta aún no tiene un rol asignado por un administrador.",
            )

        if current_user.rol not in allowed_roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return current_user

    return role_checker


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Debe ser administrador")
    return current_user
