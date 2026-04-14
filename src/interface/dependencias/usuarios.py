import os
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.add_usuario import AddUsuarios
from src.application.delete_usuario import DeleteUsuarios
from src.application.get_usuario import GetUsuarios
from src.application.update_rol import UpdateUsuarios
from src.config import settings
from src.domain.models import User
from src.infrastructure.cognito.auth_validator import CognitoTokenValidator
from src.infrastructure.cognito.cognito import CognitoRepository

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "")

if not COGNITO_USER_POOL_ID:
    raise ValueError("COGNITO_USER_POOL_ID no está configurado")

token_validator = CognitoTokenValidator(
    AWS_REGION, COGNITO_USER_POOL_ID, settings.cognito_app_client_id
)

security_scheme = HTTPBearer(auto_error=False)


def get_cognito_repo() -> CognitoRepository:
    return CognitoRepository(region=AWS_REGION, user_pool_id=COGNITO_USER_POOL_ID)


def get_usuarios_service() -> GetUsuarios:
    return GetUsuarios(repository=get_cognito_repo())


def delete_usuarios_service() -> DeleteUsuarios:
    return DeleteUsuarios(repository=get_cognito_repo())


def update_rol_service() -> UpdateUsuarios:
    return UpdateUsuarios(repository=get_cognito_repo())


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> User:
    """Valida el token contra Cognito O asume usuario de sistema si usa API Key."""

    if credentials:
        token = credentials.credentials
        user = await token_validator.verify_token(token)
        return user
    api_key = request.headers.get("X-API-KEY")
    if api_key:
        return User(
            email="sistema@microservicio.interno", nombre="Integración M2M", rol="admin"
        )

    raise HTTPException(status_code=401, detail="Credenciales no proporcionadas.")


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
