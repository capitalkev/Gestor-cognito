import boto3
from typing import List, Dict, Any
from src.domain.interfaces import IdentityRepositoryInterface

class CognitoRepository(IdentityRepositoryInterface):
    def __init__(self, region: str, user_pool_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.client = boto3.client('cognito-idp', region_name=self.region)

    def listar_usuarios(self) -> List[Dict[str, Any]]:
        response = self.client.list_users(UserPoolId=self.user_pool_id)
        usuarios = []
        for user in response.get('Users', []):
            email = next((attr['Value'] for attr in user['Attributes'] if attr['Name'] == 'email'), "N/A")
            usuarios.append({
                "username": user['Username'],
                "email": email,
                "status": user['UserStatus'],
                "enabled": user['Enabled']
            })
        return usuarios

    def crear_usuario(self, email: str, password_temporal: str) -> str:
        response = self.client.admin_create_user(
            UserPoolId=self.user_pool_id,
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'}
            ],
            TemporaryPassword=password_temporal,
            MessageAction='SUPPRESS'
        )
        return response['User']['Username']

    def asignar_rol(self, email: str, rol: str):
        self.client.admin_add_user_to_group(
            UserPoolId=self.user_pool_id,
            Username=email,
            GroupName=rol.lower()
        )
        
    def cambiar_rol_usuario(self, email: str, rol_antiguo: str, rol_nuevo: str):
        # 1. Sacar al usuario del grupo (rol) actual
        if rol_antiguo:
            try:
                self.client.admin_remove_user_from_group(
                    UserPoolId=self.user_pool_id,
                    Username=email,
                    GroupName=rol_antiguo.lower()
                )
            except self.client.exceptions.ResourceNotFoundException:
                pass # Si el grupo no existe o no estaba en él, lo ignoramos

        # 2. Añadirlo al nuevo grupo (rol)
        self.client.admin_add_user_to_group(
            UserPoolId=self.user_pool_id,
            Username=email,
            GroupName=rol_nuevo.lower()
        )

    def deshabilitar_usuario(self, email: str):
        self.client.admin_disable_user(
            UserPoolId=self.user_pool_id,
            Username=email
        )

    def habilitar_usuario(self, email: str):
        self.client.admin_enable_user(
            UserPoolId=self.user_pool_id,
            Username=email
        )

    def eliminar_usuario(self, email: str):
        self.client.admin_delete_user(
            UserPoolId=self.user_pool_id,
            Username=email
        )