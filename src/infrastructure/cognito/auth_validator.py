from typing import Any

import httpx
from fastapi import HTTPException
from jose import jwt

from src.config import settings
from src.domain.models import User


class CognitoTokenValidator:
    def __init__(self, region: str, user_pool_id: str, app_client_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.app_client_id = app_client_id
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

            try:
                claims = jwt.decode(
                    token,
                    jwks,
                    algorithms=["RS256"],
                    audience=self.app_client_id,
                    options={"verify_at_hash": False},
                )
            except Exception:
                self._jwks = {}
                jwks = await self._get_jwks()
                claims = jwt.decode(
                    token,
                    jwks,
                    algorithms=["RS256"],
                    audience=self.app_client_id,
                    options={"verify_at_hash": False},
                )

            email = claims.get("email", claims.get("username", "desconocido")).lower()

            if not any(email.endswith(dominio) for dominio in settings.parsed_domains):
                raise HTTPException(
                    status_code=403,
                    detail="Acceso denegado: El dominio corporativo no está autorizado.",
                )

            grupos_cognito = claims.get("cognito:groups", [])

            grupos_reales = [
                g.lower()
                for g in grupos_cognito
                if not g.endswith("_google") and "us-east-1" not in g
            ]

            return User(email=email, nombre=email, roles=grupos_reales)

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido") from None
