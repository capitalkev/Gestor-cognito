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
                token,
                jwks,
                algorithms=["RS256"],
                options={"verify_aud": False, "verify_at_hash": False},
            )

            # Extraemos el email primero
            email = claims.get("email", claims.get("username", "desconocido")).lower()

            dominios_permitidos = ["@capitalexpress.cl", "@capitalexpress.pe"]
            if not any(email.endswith(dominio) for dominio in dominios_permitidos):
                raise HTTPException(
                    status_code=403,
                    detail=f"Acceso denegado: El dominio del correo '{email}' no está autorizado corporativamente.",
                )

            grupos_cognito = claims.get("cognito:groups", [])

            grupos_reales = [
                g.lower()
                for g in grupos_cognito
                if not g.endswith("_google") and "us-east-1" not in g
            ]

            if "admin" in grupos_reales:
                rol_asignado = "admin"
            elif grupos_reales:
                rol_asignado = grupos_reales[0]
            else:
                rol_asignado = "sin_asignar"

            return User(email=email, nombre=email, rol=rol_asignado)

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=401, detail="Token inválido:") from None
