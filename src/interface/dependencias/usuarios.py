from capitalexpress_auth import CapitalExpressAuth

from src.application.delete_usuario import DeleteUsuarios
from src.application.get_usuario import GetUsuarios
from src.application.update_rol import UpdateUsuarios
from src.config import settings
from src.infrastructure.cognito.cognito import CognitoRepository

auth_manager = CapitalExpressAuth(
    region=settings.aws_region,
    user_pool_id=settings.cognito_user_pool_id,
    app_client_id=settings.cognito_app_client_id,
    api_keys=settings.parsed_api_keys,
)

get_current_user = auth_manager.get_current_user
require_roles = auth_manager.require_roles


def get_cognito_repo() -> CognitoRepository:
    return CognitoRepository(
        region=settings.aws_region, user_pool_id=settings.cognito_user_pool_id
    )


def get_usuarios_service() -> GetUsuarios:
    return GetUsuarios(repository=get_cognito_repo())


def delete_usuarios_service() -> DeleteUsuarios:
    return DeleteUsuarios(repository=get_cognito_repo())


def update_rol_service() -> UpdateUsuarios:
    return UpdateUsuarios(repository=get_cognito_repo())
