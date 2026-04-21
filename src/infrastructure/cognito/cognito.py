from typing import Any

import boto3
import botocore.exceptions
from fastapi import HTTPException

from src.domain.interfaces import UsuarioInterface


class CognitoRepository(UsuarioInterface):
    def __init__(self, region: str, user_pool_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.client = boto3.client("cognito-idp", region_name=self.region)

    def listar_usuarios(self) -> list[dict[str, Any]]:
        response = self.client.list_users(UserPoolId=self.user_pool_id)
        usuarios = []
        for user in response.get("Users", []):
            email = next(
                (a["Value"] for a in user["Attributes"] if a["Name"] == "email"), "N/A"
            )

            groups_resp = self.client.admin_list_groups_for_user(
                UserPoolId=self.user_pool_id, Username=user["Username"]
            )
            roles = [g["GroupName"] for g in groups_resp.get("Groups", [])]

            usuarios.append(
                {
                    "username": user["Username"],
                    "email": email,
                    "status": user["UserStatus"],
                    "enabled": user["Enabled"],
                    "roles": roles,
                }
            )
        return usuarios

    def asignar_rol(self, username: str, rol: str) -> None:
        """Agrega al usuario a un grupo de Cognito (el rol)"""
        try:
            self.client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id, Username=username, GroupName=rol
            )
        except self.client.exceptions.UserNotFoundException:
            raise HTTPException(
                status_code=404, detail=f"El usuario {username} no existe en Cognito"
            ) from None
        except botocore.exceptions.ClientError as e:
            raise HTTPException(
                status_code=400, detail=f"Error de AWS al asignar el rol: {str(e)}"
            ) from None

    def remover_rol(self, username: str, rol: str) -> None:
        """Remueve a un usuario de un grupo de Cognito"""
        if rol:
            try:
                self.client.admin_remove_user_from_group(
                    UserPoolId=self.user_pool_id, Username=username, GroupName=rol
                )
            except self.client.exceptions.UserNotFoundException:
                pass
            except botocore.exceptions.ClientError as e:
                raise HTTPException(
                    status_code=400, detail=f"Error de AWS al remover el rol: {str(e)}"
                ) from None

    def revocar_sesiones(self, username: str) -> None:
        """Fuerza el cierre de sesión en todos los dispositivos del usuario"""
        self.client.admin_user_global_sign_out(
            UserPoolId=self.user_pool_id, Username=username
        )

    def eliminar_usuario(self, email: str) -> None:
        """Elimina un usuario de Cognito"""
        try:
            self.client.admin_delete_user(UserPoolId=self.user_pool_id, Username=email)
        except self.client.exceptions.UserNotFoundException:
            raise HTTPException(
                status_code=404, detail=f"El usuario {email} no existe en Cognito"
            ) from None
        except botocore.exceptions.ClientError as e:
            raise HTTPException(
                status_code=400, detail=f"Error de AWS al eliminar el usuario: {str(e)}"
            ) from None
