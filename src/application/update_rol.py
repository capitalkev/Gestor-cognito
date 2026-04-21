from src.domain.interfaces import UsuarioInterface


class UpdateUsuarios:
    def __init__(self, repository: UsuarioInterface):
        self.repository = repository

    def asignar(self, email: str, rol: str) -> None:
        self.repository.asignar_rol(email, rol)
        self.repository.revocar_sesiones(email)

    def remover(self, email: str, rol: str) -> None:
        self.repository.remover_rol(email, rol)
        self.repository.revocar_sesiones(email)
