from src.domain.interfaces import UsuarioInterface


class UpdateUsuarios:
    def __init__(self, repository: UsuarioInterface):
        self.repository = repository

    def asignar(self, email: str, rol: str) -> None:
        return self.repository.asignar_rol(email, rol)

    def remover(self, email: str, rol: str) -> None:
        return self.repository.remover_rol(email, rol)
