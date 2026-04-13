from src.domain.interfaces import UsuarioInterface


class UpdateUsuarios:
    def __init__(self, repository: UsuarioInterface):
        self.repository = repository

    def execute(self, email: str, rol_antiguo: str, rol_nuevo: str) -> None:
        return self.repository.cambiar_rol_usuario(email, rol_antiguo, rol_nuevo)
