from src.domain.interfaces import UsuarioInterface


class DeleteUsuarios:
    def __init__(self, repository: UsuarioInterface):
        self.repository = repository

    def execute(self, email: str) -> None:
        return self.repository.eliminar_usuario(email)
