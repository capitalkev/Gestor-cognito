import os
import urllib.request
import json
from fastapi import Depends, Header, HTTPException
from jose import jwt, jwk
from jose.utils import base64url_decode

from src.domain.models import User

REGION = os.getenv("AWS_REGION", "us-east-1")
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
KEYS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

_cognito_keys = None

def get_cognito_public_keys():
    global _cognito_keys
    if not _cognito_keys:
        with urllib.request.urlopen(KEYS_URL) as response:
            _cognito_keys = json.loads(response.read().decode('utf-8'))['keys']
    return _cognito_keys

def get_current_user(authorization: str = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado o inválido")

    token = authorization.split(" ")[1]
    
    try:
        headers = jwt.get_unverified_headers(token)
        keys = get_cognito_public_keys()
        key_data = next((k for k in keys if k['kid'] == headers['kid']), None)
        
        if not key_data:
            raise HTTPException(status_code=401, detail="Llave pública no encontrada")
            
        public_key = jwk.construct(key_data)
        message, encoded_signature = str(token).rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
        
        if not public_key.verify(message.encode('utf8'), decoded_signature):
            raise HTTPException(status_code=401, detail="Firma del token inválida")
            
        claims = jwt.get_unverified_claims(token)
        grupos_cognito = claims.get("cognito:groups", [])
        rol_asignado = grupos_cognito[0].lower() if grupos_cognito else "ventas"
        email = claims.get("email", claims.get("username", "desconocido"))
        
        return User(email=email, nombre=email, rol=rol_asignado)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.rol not in allowed_roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return current_user
    return role_checker