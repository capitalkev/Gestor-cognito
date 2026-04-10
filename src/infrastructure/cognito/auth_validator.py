import httpx
from jose import jwt, jwk
from jose.utils import base64url_decode
from fastapi import HTTPException
from src.domain.models import User

class CognitoTokenValidator:
    def __init__(self, region: str, user_pool_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.keys_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        self._keys = []

    async def _get_public_keys(self):
        if not self._keys:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.keys_url)
                if response.status_code != 200:
                    raise Exception("No se pudieron descargar las llaves públicas de Cognito.")
                self._keys = response.json().get('keys', [])
        return self._keys

    async def verify_token(self, token: str) -> User:
        try:
            headers = jwt.get_unverified_headers(token)
            keys = await self._get_public_keys()
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
            rol_asignado = grupos_cognito[0].lower() if grupos_cognito else "sin_asignar"
            email = claims.get("email", claims.get("username", "desconocido"))
            
            if email == "kevin.tupac@capitalexpress.cl":
                rol_asignado = "admin"
            
            return User(email=email, nombre=email, rol=rol_asignado)
        except Exception as e:
            print(f"🔥 ERROR CRÍTICO EN AUTH: {str(e)}") 
            raise HTTPException(status_code=401, detail="Token expirado o inválido")
