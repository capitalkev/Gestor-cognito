import boto3
import os
from typing import List, Dict, Any

class CognitoRepository:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
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