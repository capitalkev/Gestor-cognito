from src.domain.interfaces import IdentityRepositoryInterface
from src.domain.models import NuevoUsuarioRequest, ActualizarRolRequest


class UsuariosService:
    def __init__(self, repo: IdentityRepositoryInterface):
        self.repo = repo

    def obtener_todos_los_usuarios(self):
        return self.repo.listar_usuarios()

    def registrar_nuevo_empleado(self, datos: NuevoUsuarioRequest):
        try:
            # 1. Creamos el usuario en AWS
            self.repo.crear_usuario(datos.email, datos.password_temporal)

            # 2. Le asignamos el rol
            self.repo.asignar_rol(datos.email, datos.rol)

            return {
                "success": True,
                "message": f"Usuario {datos.email} creado con rol {datos.rol}",
            }
        except Exception as e:
            raise ValueError(f"Error al registrar empleado: {str(e)}")

    def actualizar_rol_empleado(self, email: str, datos: ActualizarRolRequest):
        try:
            self.repo.cambiar_rol_usuario(email, datos.rol_antiguo, datos.rol_nuevo)
            return {
                "success": True,
                "message": f"Rol de {email} actualizado a {datos.rol_nuevo}",
            }
        except Exception as e:
            raise ValueError(f"Error al actualizar el rol: {str(e)}")

    def cambiar_estado_empleado(self, email: str, habilitar: bool):
        try:
            if habilitar:
                self.repo.habilitar_usuario(email)
                estado = "habilitado"
            else:
                self.repo.deshabilitar_usuario(email)
                estado = "deshabilitado"
            return {"success": True, "message": f"Usuario {email} ha sido {estado}"}
        except Exception as e:
            raise ValueError(f"Error al cambiar el estado del usuario: {str(e)}")

    def eliminar_empleado(self, email: str):
        try:
            self.repo.eliminar_usuario(email)
            return {
                "success": True,
                "message": f"Usuario {email} eliminado permanentemente",
            }
        except Exception as e:
            raise ValueError(f"Error al eliminar el usuario: {str(e)}")
