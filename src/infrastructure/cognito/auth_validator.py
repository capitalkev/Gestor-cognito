from typing import Any

import httpx
from fastapi import HTTPException
from jose import jwt

from src.domain.models import User


class CognitoTokenValidator:
    def __init__(self, region: str, user_pool_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.keys_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        self._jwks: dict[str, Any] = {}

    async def _get_jwks(self) -> dict[str, Any]:
        if not self._jwks:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.keys_url)
                if response.status_code != 200:
                    raise Exception(
                        "No se pudieron descargar las llaves públicas de Cognito."
                    )
                self._jwks = response.json()
        return self._jwks

    async def verify_token(self, token: str) -> User:
        try:
            jwks = await self._get_jwks()
            claims = jwt.decode(
                token, jwks, algorithms=["RS256"], options={"verify_aud": False}
            )

            grupos_cognito = claims.get("cognito:groups", [])
            rol_asignado = (
                grupos_cognito[0].lower() if grupos_cognito else "sin_asignar"
            )
            email = claims.get("email", claims.get("username", "desconocido"))

            return User(email=email, nombre=email, rol=rol_asignado)
        except Exception:
            raise HTTPException(
                status_code=401, detail="Token expirado o inválido"
            ) from None
