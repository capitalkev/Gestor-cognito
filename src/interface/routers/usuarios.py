from fastapi import APIRouter, Depends, HTTPException, Security

from src.application.usuarios_service import UsuariosService
from src.domain.models import ActualizarRolRequest, NuevoUsuarioRequest, User
from src.interface.dependencias.usuarios import (
    get_admin_user,
    get_current_user,
    get_usuarios_service,
    require_roles,
)

router = APIRouter(prefix="/api/admin/usuarios", tags=["Gestión de Usuarios IAM"])


@router.get("/")
def listar_empleados(
    current_user: User = Security(get_current_user, scopes=["admin"]),
    service: UsuariosService = Depends(get_usuarios_service),
):
    return service.obtener_todos_los_usuarios()


@router.post("/", dependencies=[Depends(require_roles(["admin"]))])
def crear_empleado(
    payload: NuevoUsuarioRequest,
    service: UsuariosService = Depends(get_usuarios_service),
):
    try:
        return service.registrar_nuevo_empleado(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put("/{email}/rol", dependencies=[Depends(require_roles(["admin"]))])
def actualizar_rol(
    email: str,
    payload: ActualizarRolRequest,
    service: UsuariosService = Depends(get_usuarios_service),
):
    try:
        return service.actualizar_rol_empleado(email, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put("/{email}/estado", dependencies=[Depends(require_roles(["admin"]))])
def cambiar_estado_acceso(
    email: str,
    habilitar: bool,
    service: UsuariosService = Depends(get_usuarios_service),
):
    try:
        return service.cambiar_estado_empleado(email, habilitar)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{email}")
def eliminar_usuario(
    email: str,
    admin: User = Depends(get_admin_user),
    service: UsuariosService = Depends(get_usuarios_service),
):
    return service.eliminar_empleado(email)
