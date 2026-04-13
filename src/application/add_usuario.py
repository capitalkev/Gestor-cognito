from src.domain.interfaces import UsuarioInterface


class AddUsuarios:
    def __init__(self, repository: UsuarioInterface):
        self.repository = repository

    def execute(self, email: str) -> str:
        return self.repository.crear_usuario(email, rol='Sin Rol')
