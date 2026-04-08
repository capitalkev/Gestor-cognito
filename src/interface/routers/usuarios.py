from fastapi import APIRouter, Depends, HTTPException

from src.domain.models import NuevoUsuarioRequest
from src.application.usuarios_service import UsuariosService
from src.interface.middleware.auth import require_roles

router = APIRouter(prefix="/api/admin/usuarios", tags=["Gestión de Usuarios IAM"])

def get_usuarios_service():
    return UsuariosService()

@router.get("/")
def listar_empleados(
    admin_user = Depends(require_roles(["admin"])), 
    service: UsuariosService = Depends(get_usuarios_service)
):
    """Obtiene la lista de todos los usuarios registrados en Cognito"""
    return service.obtener_todos_los_usuarios()

@router.post("/")
def crear_empleado(
    payload: NuevoUsuarioRequest,
    admin_user = Depends(require_roles(["admin"])),
    service: UsuariosService = Depends(get_usuarios_service)
):
    """Crea un nuevo usuario en AWS y le asigna su grupo/rol"""
    try:
        return service.registrar_nuevo_empleado(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))