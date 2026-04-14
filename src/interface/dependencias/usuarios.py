import os
from collections.abc import Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.add_usuario import AddUsuarios
from src.application.delete_usuario import DeleteUsuarios
from src.application.get_usuario import GetUsuarios
from src.application.update_rol import UpdateUsuarios
from src.domain.models import User
from src.infrastructure.cognito.auth_validator import CognitoTokenValidator
from src.infrastructure.cognito.cognito import CognitoRepository

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")

if not COGNITO_USER_POOL_ID:
    raise ValueError("COGNITO_USER_POOL_ID no está configurado")

token_validator = CognitoTokenValidator(AWS_REGION, COGNITO_USER_POOL_ID)

# Instanciamos el esquema de seguridad para Swagger
security_scheme = HTTPBearer()


def get_cognito_repo() -> CognitoRepository:
    return CognitoRepository(region=AWS_REGION, user_pool_id=str(COGNITO_USER_POOL_ID))


def get_usuarios_service() -> GetUsuarios:
    return GetUsuarios(repository=get_cognito_repo())


def add_usuarios_service() -> AddUsuarios:
    return AddUsuarios(repository=get_cognito_repo())


def delete_usuarios_service() -> DeleteUsuarios:
    return DeleteUsuarios(repository=get_cognito_repo())


def update_rol_service() -> UpdateUsuarios:
    return UpdateUsuarios(repository=get_cognito_repo())


# 1. AUTENTICACIÓN: Solo se encarga de saber QUIÉN es el usuario
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> User:
    """Extrae el token Bearer y valida el usuario contra Cognito."""
    token = credentials.credentials
    user = await token_validator.verify_token(token)
    return user


# 2. AUTORIZACIÓN: Se encarga de saber si el usuario PUEDE hacer la acción
def require_roles(allowed_roles: list[str]) -> Callable[..., User]:
    """Fábrica de dependencias para validar roles específicos."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.rol == "sin_asignar":
            raise HTTPException(
                status_code=403,
                detail="Tu cuenta aún no tiene un rol asignado por un administrador.",
            )

        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=403, detail="Permisos insuficientes para esta acción."
            )

        return current_user

    return role_checker
