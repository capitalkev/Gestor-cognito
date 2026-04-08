from src.domain.models import NuevoUsuarioRequest
from src.infrastructure.cognito.cognito import CognitoRepository

class UsuariosService:
    def __init__(self):
        self.repo = CognitoRepository()

    def obtener_todos_los_usuarios(self):
        return self.repo.listar_usuarios()

    def registrar_nuevo_empleado(self, datos: NuevoUsuarioRequest):
        try:
            # 1. Creamos el usuario en AWS
            self.repo.crear_usuario(datos.email, datos.password_temporal)
            
            # 2. Le asignamos el rol
            self.repo.asignar_rol(datos.email, datos.rol)
            
            return {"success": True, "message": f"Usuario {datos.email} creado con rol {datos.rol}"}
        except Exception as e:
            raise ValueError(f"Error al registrar empleado: {str(e)}")