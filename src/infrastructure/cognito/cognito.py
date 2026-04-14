from typing import Any

import boto3
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
                    "roles": roles if roles else ["sin_asignar"],
                }
            )
        return usuarios

    def asignar_rol(self, email: str, rol: str) -> None:
        """Agrega al usuario a un grupo de Cognito (el rol)"""
        self.client.admin_add_user_to_group(
            UserPoolId=self.user_pool_id, Username=email, GroupName=rol.lower()
        )

    def cambiar_rol_usuario(self, email: str, rol_antiguo: str, rol_nuevo: str) -> None:
        """Mueve a un usuario de un grupo a otro de forma atómica"""
        if rol_antiguo and rol_antiguo != "sin_asignar":
            self.client.admin_remove_user_from_group(
                UserPoolId=self.user_pool_id,
                Username=email,
                GroupName=rol_antiguo.lower(),
            )
        if rol_nuevo != "sin_asignar":
            self.asignar_rol(email, rol_nuevo)

    def eliminar_usuario(self, email: str) -> None:
        self.client.admin_delete_user(UserPoolId=self.user_pool_id, Username=email)

    def crear_usuario(self, email: str, rol: str = "Sin Rol") -> str:
        """Crea un usuario en Cognito y le asigna un rol inicial con manejo de errores."""
        try:
            response = self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "email_verified", "Value": "true"},
                ],
                MessageAction="SUPPRESS",
            )

            username = response["User"]["Username"]

            if rol and rol.lower() != "sin_asignar":
                self.asignar_rol(username, rol)

            return username

        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve)) from None
