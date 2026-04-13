from typing import Any

from fastapi import APIRouter, Depends, Security

from src.application.add_usuario import AddUsuarios
from src.application.delete_usuario import DeleteUsuarios
from src.application.get_usuario import GetUsuarios
from src.application.update_rol import UpdateUsuarios
from src.domain.models import User
from src.interface.dependencias.usuarios import (
    add_usuarios_service,
    delete_usuarios_service,
    get_admin_user,
    get_current_user,
    get_usuarios_service,
    require_roles,
    update_rol_service,
)

router = APIRouter(prefix="/api/admin/usuarios", tags=["Gestión de Usuarios IAM"])


@router.get("/")
def listar_empleados(
    current_user: User = Security(get_current_user, scopes=["admin"]),
    service: GetUsuarios = Depends(get_usuarios_service),
) -> list[dict[str, Any]]:
    return service.execute()


@router.post("/", dependencies=[Depends(require_roles(["admin"]))])
def crear_empleado(
    email: str,
    service: AddUsuarios = Depends(add_usuarios_service),
) -> str:
    return service.execute(email)


@router.put("/{email}/rol", dependencies=[Depends(require_roles(["admin"]))])
def actualizar_rol(
    email: str,
    rol_antiguo: str,
    rol_nuevo: str,
    service: UpdateUsuarios = Depends(update_rol_service),
) -> None:
    return service.execute(email, rol_antiguo, rol_nuevo)


@router.delete("/{email}")
def eliminar_usuario(
    email: str,
    admin: User = Depends(get_admin_user),
    service: DeleteUsuarios = Depends(delete_usuarios_service),
) -> None:
    return service.execute(email)
