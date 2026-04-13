from typing import Any

from src.domain.interfaces import UsuarioInterface


class GetUsuarios:
    def __init__(self, repository: UsuarioInterface):
        self.repository = repository

    def execute(self) -> list[dict[str, Any]]:
        return self.repository.listar_usuarios()
