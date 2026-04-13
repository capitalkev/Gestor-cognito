from fastapi import APIRouter, Depends, HTTPException

from src.application.usuarios_service import UsuariosService
from src.domain.models import ActualizarRolRequest, NuevoUsuarioRequest
from src.interface.dependencias.usuarios import get_usuarios_service, require_roles

router = APIRouter(prefix="/api/admin/usuarios", tags=["Gestión de Usuarios IAM"])


@router.get("/")
def listar_empleados(
    admin_user=Depends(require_roles(["admin"])),
    service: UsuariosService = Depends(get_usuarios_service),
)-> None:
    return service.obtener_todos_los_usuarios()


@router.post("/")
def crear_empleado(
    payload: NuevoUsuarioRequest,
    admin_user=Depends(require_roles(["admin"])),
    service: UsuariosService = Depends(get_usuarios_service),
):
    """Crea un nuevo usuario en AWS y le asigna su grupo/rol"""
    try:
        return service.registrar_nuevo_empleado(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put("/{email}/rol")
def actualizar_rol(
    email: str,
    payload: ActualizarRolRequest,
    admin_user=Depends(require_roles(["admin"])),
    service: UsuariosService = Depends(get_usuarios_service),
):
    """Actualiza el rol (grupo) de un usuario existente"""
    try:
        return service.actualizar_rol_empleado(email, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put("/{email}/estado")
def cambiar_estado_acceso(
    email: str,
    habilitar: bool,
    admin_user=Depends(require_roles(["admin"])),
    service: UsuariosService = Depends(get_usuarios_service),
):
    """Habilita o deshabilita el acceso de un usuario a la plataforma"""
    try:
        return service.cambiar_estado_empleado(email, habilitar)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{email}")
def eliminar_usuario(
    email: str,
    admin_user=Depends(require_roles(["admin"])),
    service: UsuariosService = Depends(get_usuarios_service),
):
    """Elimina permanentemente a un usuario del User Pool de Cognito"""
    try:
        return service.eliminar_empleado(email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
